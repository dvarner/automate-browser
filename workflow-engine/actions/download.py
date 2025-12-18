"""Download actions for files, links, and media"""

import os
import time
import requests
from pathlib import Path
from .base import BaseAction


class DownloadAction(BaseAction):
    """
    Click element and wait for browser download to complete
    Works for download buttons/links that trigger browser downloads
    """

    def description(self):
        selector = self.step.get('selector', 'element')
        destination = self.step.get('destination', 'default location')
        return f"Download from {selector} to {destination}"

    def execute(self):
        selector = self.step.get('selector')
        if not selector:
            raise ValueError("Download action requires 'selector' field")

        # Optional parameters
        save_as = self.step.get('save_as')  # Custom filename
        destination = self.step.get('destination', 'results')  # Destination folder
        timeout = self.step.get('timeout', 60)  # Download timeout in seconds

        # Ensure destination directory exists
        dest_path = Path(destination)
        dest_path.mkdir(parents=True, exist_ok=True)

        # Wait for download to start when element is clicked
        with self.page.expect_download(timeout=timeout * 1000) as download_info:
            # Click the element that triggers download
            self.page.click(selector)

        download = download_info.value

        # Determine save path
        if save_as:
            save_path = dest_path / save_as
        else:
            # Use original filename
            save_path = dest_path / download.suggested_filename

        # Save the download
        download.save_as(save_path)

        # Store download info in data_store
        download_name = self.step.get('name', 'last_download')
        self.data_store[download_name] = {
            'path': str(save_path),
            'filename': save_path.name,
            'size': save_path.stat().st_size if save_path.exists() else 0
        }

        return f"Downloaded to {save_path} ({save_path.stat().st_size:,} bytes)"


class DownloadLinkAction(BaseAction):
    """
    Download file from a link without clicking
    Extracts href and downloads programmatically to custom location
    """

    def description(self):
        selector = self.step.get('selector', 'link')
        destination = self.step.get('destination', 'default location')
        return f"Download link {selector} to {destination}"

    def execute(self):
        selector = self.step.get('selector')
        if not selector:
            raise ValueError("Download_link action requires 'selector' field")

        # Optional parameters
        save_as = self.step.get('save_as')  # Custom filename
        destination = self.step.get('destination', 'results')  # Destination folder
        timeout = self.step.get('timeout', 60)  # Download timeout in seconds

        # Ensure destination directory exists
        dest_path = Path(destination)
        dest_path.mkdir(parents=True, exist_ok=True)

        # Get the link URL (try visible first, then any state)
        try:
            element = self.page.wait_for_selector(selector, state='visible', timeout=timeout * 1000)
        except Exception:
            # If element not visible, try to get it anyway
            element = self.page.wait_for_selector(selector, state='attached', timeout=timeout * 1000)

        href = element.get_attribute('href')

        if not href:
            raise ValueError(f"Element {selector} has no href attribute")

        # Handle relative URLs
        if href.startswith('/') or not href.startswith('http'):
            base_url = self.page.url
            from urllib.parse import urljoin
            href = urljoin(base_url, href)

        # Determine filename
        if save_as:
            filename = save_as
        else:
            # Extract filename from URL
            filename = href.split('/')[-1].split('?')[0]
            if not filename:
                filename = 'download'

        save_path = dest_path / filename

        # Download the file using requests
        print(f"    📥 Downloading from {href}")

        response = requests.get(href, timeout=timeout, stream=True)
        response.raise_for_status()

        # Save to file
        total_size = 0
        with open(save_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    total_size += len(chunk)

        # Store download info
        download_name = self.step.get('name', 'last_download')
        self.data_store[download_name] = {
            'path': str(save_path),
            'filename': save_path.name,
            'url': href,
            'size': total_size
        }

        return f"Downloaded {href} to {save_path} ({total_size:,} bytes)"


class DownloadMediaAction(BaseAction):
    """
    Download image or video from page
    Extracts src attribute and downloads to custom location
    """

    def description(self):
        selector = self.step.get('selector', 'media')
        media_type = self.step.get('type', 'media')
        destination = self.step.get('destination', 'default location')
        return f"Download {media_type} {selector} to {destination}"

    def execute(self):
        selector = self.step.get('selector')
        if not selector:
            raise ValueError("Download_media action requires 'selector' field")

        # Optional parameters
        media_type = self.step.get('type', 'image')  # 'image' or 'video'
        save_as = self.step.get('save_as')  # Custom filename
        destination = self.step.get('destination', 'results')  # Destination folder
        timeout = self.step.get('timeout', 60)  # Download timeout in seconds

        # Ensure destination directory exists
        dest_path = Path(destination)
        dest_path.mkdir(parents=True, exist_ok=True)

        # Get the media element (try visible first, then any state)
        try:
            element = self.page.wait_for_selector(selector, state='visible', timeout=timeout * 1000)
        except Exception:
            # If element not visible, try to get it anyway
            element = self.page.wait_for_selector(selector, state='attached', timeout=timeout * 1000)

        # Get source URL (try src, then data-src for lazy-loaded images)
        src = element.get_attribute('src')
        if not src:
            src = element.get_attribute('data-src')
        if not src:
            raise ValueError(f"Element {selector} has no src or data-src attribute")

        # Handle relative URLs
        if src.startswith('/') or not src.startswith('http'):
            base_url = self.page.url
            from urllib.parse import urljoin
            src = urljoin(base_url, src)

        # Determine filename
        if save_as:
            filename = save_as
        else:
            # Extract filename from URL
            filename = src.split('/')[-1].split('?')[0]
            if not filename or '.' not in filename:
                # Generate filename with appropriate extension
                ext = 'jpg' if media_type == 'image' else 'mp4'
                filename = f"{media_type}_{int(time.time())}.{ext}"

        save_path = dest_path / filename

        # Download the media file
        print(f"    📥 Downloading {media_type} from {src}")

        response = requests.get(src, timeout=timeout, stream=True)
        response.raise_for_status()

        # Save to file
        total_size = 0
        with open(save_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    total_size += len(chunk)

        # Store download info
        download_name = self.step.get('name', 'last_download')
        self.data_store[download_name] = {
            'path': str(save_path),
            'filename': save_path.name,
            'url': src,
            'type': media_type,
            'size': total_size
        }

        return f"Downloaded {media_type} to {save_path} ({total_size:,} bytes)"
