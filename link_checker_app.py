#!/usr/bin/env python3
"""
Link Checker Streamlit App
Checks multiple URLs for broken links, redirects, and errors
Only shows pages with issues - clean pages are skipped
"""

import streamlit as st
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from typing import List, Optional
import time

@dataclass
class LinkIssue:
    """Data class for storing link issues"""
    source_page: str
    link_url: str
    anchor_text: str
    status_code: int
    issue_type: str  # 'broken', 'redirect', 'error'
    redirect_url: Optional[str] = None
    error_message: Optional[str] = None

class LinkChecker:
    """Main class for checking links on pages"""
    
    def __init__(self, timeout: int = 10, max_workers: int = 10):
        self.timeout = timeout
        self.max_workers = max_workers
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def extract_links(self, url: str) -> List[tuple]:
        """Extract all links from a page with their anchor text"""
        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            links = []
            
            # Find all anchor tags with href
            for anchor in soup.find_all('a', href=True):
                href = anchor.get('href', '').strip()
                
                # Skip empty hrefs, javascript:, mailto:, tel:, etc.
                if not href or href.startswith(('#', 'javascript:', 'mailto:', 'tel:')):
                    continue
                
                # Convert relative URLs to absolute
                full_url = urljoin(url, href)
                
                # Get anchor text
                anchor_text = anchor.get_text().strip()
                if not anchor_text:
                    anchor_text = '[No anchor text]'
                
                # Store original href and full URL
                links.append((full_url, href, anchor_text))
            
            return links
            
        except Exception as e:
            st.error(f"Error extracting links from {url}: {e}")
            return []
    
    def check_link_status(self, link_url: str) -> dict:
        """Check the status of a single link"""
        try:
            # Use HEAD request first (faster), fall back to GET if needed
            response = self.session.head(link_url, timeout=self.timeout, allow_redirects=False)
            
            # Some servers don't support HEAD, try GET if we get 405
            if response.status_code == 405:
                response = self.session.get(link_url, timeout=self.timeout, allow_redirects=False, stream=True)
            
            result = {
                'status_code': response.status_code,
                'redirect_url': response.headers.get('Location') if response.is_redirect else None,
                'error': None
            }
            
            return result
            
        except requests.exceptions.Timeout:
            return {'status_code': 0, 'redirect_url': None, 'error': 'Timeout'}
        except requests.exceptions.ConnectionError:
            return {'status_code': 0, 'redirect_url': None, 'error': 'Connection Error'}
        except requests.exceptions.TooManyRedirects:
            return {'status_code': 0, 'redirect_url': None, 'error': 'Too Many Redirects'}
        except Exception as e:
            return {'status_code': 0, 'redirect_url': None, 'error': str(e)}
    
    def is_problematic(self, status_code: int, error: Optional[str]) -> tuple:
        """Determine if a link is problematic and categorize it"""
        if error:
            return True, 'error'
        elif status_code == 404:
            return True, 'broken'
        elif status_code in [301, 302, 303, 307, 308]:
            return True, 'redirect'
        elif status_code >= 400:
            return True, 'broken'
        elif status_code == 0:
            return True, 'error'
        return False, None
    
    def check_page_links(self, page_url: str) -> List[LinkIssue]:
        """Check all links on a single page and return only issues"""
        issues = []
        
        # Extract all links from the page
        links = self.extract_links(page_url)
        
        if not links:
            return issues
        
        # Check each link
        for full_url, original_href, anchor_text in links:
            status_info = self.check_link_status(full_url)
            
            is_problem, issue_type = self.is_problematic(
                status_info['status_code'], 
                status_info['error']
            )
            
            if is_problem:
                issue = LinkIssue(
                    source_page=page_url,
                    link_url=original_href,
                    anchor_text=anchor_text[:100],  # Limit length
                    status_code=status_info['status_code'],
                    issue_type=issue_type,
                    redirect_url=status_info['redirect_url'],
                    error_message=status_info['error']
                )
                issues.append(issue)
            
            # Small delay to be respectful
            time.sleep(0.1)
        
        return issues
    
    def check_multiple_pages(self, urls: List[str], progress_callback=None) -> List[LinkIssue]:
        """Check multiple pages concurrently"""
        all_issues = []
        total = len(urls)
        
        with ThreadPoolExecutor(max_workers=min(5, total)) as executor:
            # Submit all tasks
            future_to_url = {
                executor.submit(self.check_page_links, url): url 
                for url in urls
            }
            
            # Process completed tasks
            for i, future in enumerate(as_completed(future_to_url), 1):
                url = future_to_url[future]
                try:
                    issues = future.result()
                    if issues:  # Only add if there are issues
                        all_issues.extend(issues)
                    
                    if progress_callback:
                        progress_callback(i, total, url)
                        
                except Exception as e:
                    st.error(f"Error processing {url}: {e}")
        
        return all_issues


def main():
    """Main Streamlit app"""
    st.set_page_config(page_title="Avalara Link Checker", page_icon="🔗", layout="wide")
    
    st.title("🔗 Avalara Marketing Digital Experience Link Checker Dashboard")
    st.markdown("Check multiple pages for broken links, redirects, and errors. Only problematic links are shown.")
    
    # Sidebar for input
    with st.sidebar:
        st.header("Input URLs")
        st.markdown("Paste URLs (one per line, max 100)")
        
        url_input = st.text_area(
            "URLs to check:",
            height=300,
            placeholder="https://example.com/page1\nhttps://example.com/page2\n...",
            help="Enter up to 100 URLs, one per line"
        )
        
        timeout = st.slider("Timeout (seconds)", 5, 30, 10)
        
        check_button = st.button("🔍 Check Links", type="primary", use_container_width=True)
    
    # Main content area
    if check_button:
        # Parse URLs
        urls = [url.strip() for url in url_input.split('\n') if url.strip()]
        
        if not urls:
            st.warning("Please enter at least one URL")
            return
        
        if len(urls) > 100:
            st.warning(f"Too many URLs ({len(urls)}). Only checking the first 100.")
            urls = urls[:100]
        
        st.info(f"Checking {len(urls)} page(s) for broken links...")
        
        # Progress tracking
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        def update_progress(current, total, url):
            progress = current / total
            progress_bar.progress(progress)
            status_text.text(f"Checked {current}/{total} pages... ({url[:60]}...)")
        
        # Initialize checker and run
        checker = LinkChecker(timeout=timeout)
        issues = checker.check_multiple_pages(urls, progress_callback=update_progress)
        
        # Clear progress indicators
        progress_bar.empty()
        status_text.empty()
        
        # Display results
        if not issues:
            st.success("✅ No issues found! All checked pages have clean links.")
        else:
            st.error(f"⚠️ Found {len(issues)} problematic link(s) across {len(set(i.source_page for i in issues))} page(s)")
            
            # Convert to DataFrame
            df = pd.DataFrame([
                {
                    'Source Page': issue.source_page,
                    'Link URL': issue.link_url,
                    'Anchor Text': issue.anchor_text,
                    'Issue Type': issue.issue_type.upper(),
                    'Status Code': issue.status_code if issue.status_code else 'N/A',
                    'Redirect To': issue.redirect_url if issue.redirect_url else '',
                    'Error': issue.error_message if issue.error_message else ''
                }
                for issue in issues
            ])
            
            # Summary metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Issues", len(issues))
            with col2:
                broken_count = len([i for i in issues if i.issue_type == 'broken'])
                st.metric("Broken Links (404+)", broken_count)
            with col3:
                redirect_count = len([i for i in issues if i.issue_type == 'redirect'])
                st.metric("Redirects (301/302)", redirect_count)
            with col4:
                error_count = len([i for i in issues if i.issue_type == 'error'])
                st.metric("Errors/Timeouts", error_count)
            
            st.markdown("---")
            
            # Filters
            col1, col2 = st.columns([1, 3])
            with col1:
                filter_option = st.selectbox(
                    "Filter by Issue Type:",
                    ["All", "Broken", "Redirect", "Error"]
                )
            
            # Apply filter
            if filter_option != "All":
                df_filtered = df[df['Issue Type'] == filter_option.upper()]
            else:
                df_filtered = df
            
            # Display table
            st.dataframe(
                df_filtered,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Source Page": st.column_config.LinkColumn("Source Page", width="medium"),
                    "Link URL": st.column_config.TextColumn("Link URL", width="medium"),
                    "Anchor Text": st.column_config.TextColumn("Anchor Text", width="medium"),
                    "Issue Type": st.column_config.TextColumn("Issue Type", width="small"),
                    "Status Code": st.column_config.TextColumn("Status", width="small"),
                    "Redirect To": st.column_config.TextColumn("Redirect To", width="medium"),
                    "Error": st.column_config.TextColumn("Error", width="medium"),
                }
            )
            
            # CSV Export
            st.markdown("---")
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download Results as CSV",
                data=csv,
                file_name=f"link_check_results_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True
            )
            
            # Detailed breakdown by page
            st.markdown("---")
            st.subheader("📋 Breakdown by Page")
            
            for source_page in sorted(set(i.source_page for i in issues)):
                page_issues = [i for i in issues if i.source_page == source_page]
                with st.expander(f"🔗 {source_page} ({len(page_issues)} issues)"):
                    page_df = df[df['Source Page'] == source_page]
                    st.dataframe(page_df, use_container_width=True, hide_index=True)
    
    else:
        # Instructions when no check has been run
        st.info("👈 Enter URLs in the sidebar and click 'Check Links' to start")
        
        st.markdown("""
        ### How it works:
        1. **Paste URLs** in the sidebar (up to 100 URLs, one per line)
        2. **Click 'Check Links'** to start scanning
        3. **View results** - Only pages with issues will be shown
        4. **Export to CSV** for further analysis
        
        ### What gets checked:
        - ✅ **Broken links** (404, 5xx errors)
        - ✅ **Redirects** (301, 302, etc.)
        - ✅ **Timeouts and connection errors**
        - ✅ **Both relative and absolute URLs**
        
        ### What's shown:
        - Source page URL
        - Problematic link URL (as it appears on the page)
        - Anchor text (to help you locate the link)
        - Issue type and status code
        - Redirect destination (if applicable)
        
        **Note:** Pages with no issues are automatically skipped from the output.
        """)


if __name__ == "__main__":
    main()

