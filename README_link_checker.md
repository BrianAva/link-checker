# 🔗 Link Checker Dashboard

A clean, efficient Streamlit web application for checking broken links, redirects, and errors across multiple web pages. Designed for digital producers, content managers, and SEO professionals who need reliable link validation at scale.

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![Streamlit](https://img.shields.io/badge/streamlit-1.28+-red.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## ✨ Features

- **Batch Processing**: Check up to 100 URLs simultaneously
- **Smart Filtering**: Only displays problematic links - clean pages are automatically skipped
- **Comprehensive Detection**: 
  - 🔴 Broken links (404, 5xx errors)
  - 🟡 Redirects (301, 302, 307, 308)
  - 🔴 Connection errors and timeouts
- **Detailed Context**: Shows anchor text and link location to help locate issues quickly
- **Interactive Dashboard**: 
  - Real-time progress tracking
  - Summary metrics
  - Filterable results table
  - Expandable sections grouped by source page
- **CSV Export**: Download results with timestamp for documentation
- **Reliable**: Uses `requests` + `BeautifulSoup` (no browser dependencies)

## 🎯 Why This Tool?

Unlike browser extensions that can be unreliable or inconsistent, this tool provides:
- **Consistent Results**: Server-side validation with proper HTTP status codes
- **Batch Efficiency**: Check multiple pages in one session
- **Exportable Reports**: CSV output for documentation and tracking
- **Context for Fixes**: Anchor text helps digital producers locate exact link positions
- **Clean Output**: Only shows what needs fixing - no noise

## 📋 Prerequisites

- Python 3.8 or higher
- Internet connection
- Modern web browser (for viewing the Streamlit interface)

## 🚀 Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd link-checker-dashboard
```

### 2. Install Dependencies

#### Using pip:

```bash
pip install -r link_checker_requirements.txt
```

#### Manual installation:

```bash
pip install streamlit requests beautifulsoup4 pandas lxml
```

### 3. Verify Installation

```bash
python -c "import streamlit; import requests; import bs4; import pandas; print('All dependencies installed successfully!')"
```

## 💻 Usage

### Starting the App

```bash
streamlit run link_checker_app.py
```

The app will automatically open in your default browser at `http://localhost:8501`

### Using the App

1. **Enter URLs**
   - Paste URLs in the sidebar text area (one per line)
   - Maximum 100 URLs per check
   - Format: Full URLs including protocol (https://example.com)

2. **Configure Settings**
   - Adjust timeout slider (5-30 seconds)
   - Higher timeout for slower servers

3. **Run Check**
   - Click "🔍 Check Links" button
   - Watch real-time progress
   - Results appear automatically

4. **Review Results**
   - View summary metrics at top
   - Filter by issue type (All, Broken, Redirect, Error)
   - Expand individual pages for details
   - Use anchor text to locate links on page

5. **Export Results**
   - Click "📥 Download Results as CSV"
   - Timestamped filename for easy tracking

### Example Input

```
https://www.avalara.com/page1
https://www.avalara.com/about
https://www.avalara.com/contact
https://www.example.com/blog/post-1
```

### Example Output

The dashboard will show:

| Source Page | Link URL | Anchor Text | Issue Type | Status Code | Redirect To |
|-------------|----------|-------------|------------|-------------|-------------|
| https://example.com/page1 | /old-page | Learn More | BROKEN | 404 | |
| https://example.com/page1 | /resources | Resources | REDIRECT | 301 | https://example.com/new-resources |
| https://example.com/about | https://oldsite.com | Visit Site | ERROR | 0 | Timeout |

## 📊 Understanding Results

### Issue Types

- **BROKEN**: 404 errors or server errors (5xx)
  - Action: Fix or remove the link
  
- **REDIRECT**: 301, 302, 307, 308 redirects
  - Action: Update link to point directly to final destination
  
- **ERROR**: Timeouts, connection failures
  - Action: Check if URL is valid, increase timeout, or remove

### Status Codes

- **404**: Page not found
- **301/302**: Permanent/temporary redirect
- **500/502/503**: Server errors
- **0**: Connection failed (timeout, DNS error, etc.)

### CSV Export Format

```csv
Source Page,Link URL,Anchor Text,Issue Type,Status Code,Redirect To,Error
https://example.com,/broken-page,Click Here,BROKEN,404,,
https://example.com,/old-url,Learn More,REDIRECT,301,https://example.com/new-url,
```

## ⚙️ Configuration

### Timeout Settings

Default: 10 seconds

- **Short timeout (5-10s)**: Fast checking, may miss slow-loading pages
- **Long timeout (15-30s)**: More thorough, takes longer

### Concurrent Requests

Default: 5 concurrent page checks

To modify, edit in `link_checker_app.py`:

```python
with ThreadPoolExecutor(max_workers=min(5, total)) as executor:  # Change 5 to desired number
```

### Link Delay

Default: 0.1 seconds between link checks

To modify, edit in `link_checker_app.py`:

```python
time.sleep(0.1)  # Change delay as needed
```

## 🏗️ Project Structure

```
.
├── link_checker_app.py              # Main Streamlit application
├── link_checker_requirements.txt    # Python dependencies
└── README.md                        # This file
```

## 🔧 Technical Details

### Architecture

- **Frontend**: Streamlit web interface
- **HTTP Client**: Python `requests` library
- **HTML Parser**: BeautifulSoup4 with lxml parser
- **Concurrency**: ThreadPoolExecutor for parallel page processing
- **Data Handling**: Pandas for data manipulation and export

### How It Works

1. **Link Extraction**: 
   - Fetches source page HTML
   - Parses all `<a>` tags with `href` attributes
   - Converts relative URLs to absolute
   - Extracts anchor text for context

2. **Link Validation**:
   - Sends HEAD request (faster) to each link
   - Falls back to GET if HEAD not supported
   - Follows redirect chain
   - Records status codes and errors

3. **Issue Detection**:
   - Identifies problematic status codes (4xx, 5xx)
   - Detects redirects (3xx)
   - Catches connection errors and timeouts

4. **Smart Filtering**:
   - Only reports pages with issues
   - Skips clean pages completely
   - Groups results by source page

### Performance

- Checks ~10-20 pages per minute (depending on page size and link count)
- Handles 100 URLs with 50+ links each efficiently
- Memory efficient - streams results as they complete

## 🛠️ Troubleshooting

### Common Issues

**"No module named 'streamlit'"**
```bash
pip install -r link_checker_requirements.txt
```

**"Connection timeout" errors**
- Increase timeout in sidebar
- Check your internet connection
- Some sites may block automated requests

**"Too many URLs" warning**
- Limit to 100 URLs per batch
- Split large lists into multiple checks

**App doesn't open automatically**
- Manually navigate to `http://localhost:8501`
- Check if port 8501 is available

**403/Blocked errors**
- Some sites block automated requests
- Tool uses common User-Agent string
- May need to whitelist or add delays

## 🚦 Best Practices

1. **Start Small**: Test with 5-10 URLs first
2. **Reasonable Timeouts**: Use 10-15 seconds for most sites
3. **Respectful Checking**: Don't hammer servers - built-in delays help
4. **Regular Checks**: Schedule periodic link audits
5. **Export Results**: Keep CSV records for tracking over time

## 📈 Use Cases

- **Content Audits**: Find and fix broken links in documentation
- **SEO Maintenance**: Identify redirect chains hurting SEO
- **Quality Assurance**: Pre-launch checks for new sites
- **Migration Validation**: Verify links after site moves
- **Competitor Analysis**: Check competitor site health (responsibly)

## 🤝 Contributing

Contributions are welcome! Here's how:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Development Setup

```bash
# Clone your fork
git clone <your-fork-url>
cd link-checker-dashboard

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r link_checker_requirements.txt

# Run in development mode
streamlit run link_checker_app.py --server.runOnSave true
```

## 📝 Changelog

### Version 1.0.0 (Initial Release)
- ✨ Batch URL checking (up to 100 URLs)
- ✨ Broken link detection (404, 5xx)
- ✨ Redirect detection (301, 302, etc.)
- ✨ Error detection (timeouts, connection errors)
- ✨ Interactive dashboard with filtering
- ✨ CSV export functionality
- ✨ Real-time progress tracking
- ✨ Smart output (only shows issues)

## 🗺️ Roadmap

Potential future enhancements:

- [ ] Historical tracking and comparison
- [ ] Scheduled automated checks
- [ ] Email notifications for broken links
- [ ] Integration with Google Search Console
- [ ] Support for sitemap.xml input
- [ ] Advanced filtering (by domain, status code, etc.)
- [ ] Bulk URL import from CSV
- [ ] API endpoint for programmatic access

## 📄 License

This project is licensed under the MIT License - see below for details:

```
MIT License

Copyright (c) 2025

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## 👤 Author

**Your Name**
- Github: (https://github.com/BrianAva/)


## 🙏 Acknowledgments

- Built with [Streamlit](https://streamlit.io/)
- Powered by [Beautiful Soup](https://www.crummy.com/software/BeautifulSoup/)
- HTTP requests via [Requests](https://requests.readthedocs.io/)

## 📞 Support

If you encounter issues or have questions:

1. Check the [Troubleshooting](#-troubleshooting) section
2. Search existing issues on GitLab
3. Open a new issue with:
   - Python version
   - Error message
   - Steps to reproduce
   - Example URL (if not sensitive)

---

**Made with ❤️ for digital producers and content teams**


