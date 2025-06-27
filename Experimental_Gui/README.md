# NN-Downloader v2.0

A modern, async multi-site media downloader with an intuitive GUI interface. Download images and media from various adult content sites with advanced features like proxy support, rate limiting, and concurrent downloads.

## Features

- **Multi-site Support**: Download from e621, e6ai, e926, Furbooru, Rule34, Luscious, Multporn, and Yiffer
- **Async Downloads**: Fast concurrent downloading with configurable limits
- **GUI Interface**: User-friendly Tkinter-based interface
- **Proxy Support**: Built-in proxy management and rotation
- **Rate Limiting**: Respectful downloading with configurable rate limits
- **Tag-based Downloads**: Search and download by tags or specific URLs
- **Blacklist Support**: Filter out unwanted content by tags or file formats
- **Progress Tracking**: Real-time download progress and task management

## Supported Sites

- **e621**: Popular furry art archive
- **e6ai**: AI-generated content variant
- **e926**: Safe-for-work version of e621
- **Furbooru**: Community-driven furry image board
- **Rule34**: General adult content site
- **Luscious**: Adult comics and images
- **Multporn**: Adult comic archive
- **Yiffer**: Furry comic platform

## Installation

### Prerequisites

- Python 3.8 or higher
- tkinter (usually included with Python)

### Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/nn-downloader.git
cd nn-downloader
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python main.py
```

## Usage

### GUI Mode (Recommended)

Simply run `python main.py` to launch the graphical interface where you can:

- Select which sites to download from
- Enter URLs or search tags
- Configure download settings
- Monitor download progress
- Manage download queues

### Configuration

The application uses `config.json` for settings. Key configuration options:

- **Site Settings**: Enable/disable sites and set rate limits
- **Download Settings**: Concurrent downloads, timeouts, and output directory
- **Proxy Settings**: Enable proxy support with automatic rotation
- **Blacklists**: Filter content by tags or file formats

### Example Configuration

```json
{
  "download": {
    "concurrent_downloads": 3,
    "output_directory": "media",
    "timeout": 30
  },
  "proxy": {
    "enabled": false,
    "test_on_startup": true
  },
  "blacklisted_tags": ["gore", "scat"],
  "blacklisted_formats": ["swf"]
}
```

## Project Structure

```
nn-downloader/
├── main.py                    # Entry point
├── config.json              # Configuration file
├── requirements.txt          # Dependencies
├── gui/
│   └── tkinter_app.py       # GUI implementation
├── downloaders/             # Site-specific downloaders
│   ├── base_async.py       # Base downloader class
│   ├── e621_async.py       # e621 downloader
│   ├── furbooru_async.py   # Furbooru downloader
│   └── ...                 # Other site downloaders
└── utils/                   # Utility modules
    ├── config_manager_async.py
    ├── directory_manager_async.py
    └── proxy_manager_async.py
```

## Development

### Architecture

- **Async-first**: Built with asyncio for efficient concurrent operations
- **Modular Design**: Each site has its own downloader module
- **Clean Separation**: GUI, downloaders, and utilities are separated
- **Type Hints**: Full type annotation support

### Adding New Sites

1. Create a new downloader in `downloaders/` inheriting from `BaseAsyncDownloader`
2. Implement required methods for the site's API
3. Add site configuration to `config.json`
4. Update the GUI to include the new site

## Requirements

- **aiohttp**: Async HTTP client
- **aiofiles**: Async file operations
- **tkinter**: GUI framework (included with Python)

## Legal Notice

This tool is for educational purposes only. Users are responsible for ensuring their use complies with:

- Site terms of service
- Local laws and regulations
- Copyright and intellectual property rights
- Content policies

Always respect rate limits and website terms when downloading content.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Changelog

### v2.0.0
- Complete rewrite with async architecture
- New GUI interface
- Enhanced proxy support
- Improved error handling
- Added more sites
- Better configuration management