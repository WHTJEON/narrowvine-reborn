# NARROWVINE-REBORN
[![made-with-python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/)

## (2021.08) Due to the New Widevine WhiteBox Exploit by Satsuoni, <br>NARROWVINE earned its second life.

The Ultimate Widevine Content Ripper (KEY Extract + Download + Decrypt)<br>
**Extracting decryption keys now supports all platforms (Mac, Windows, Linux)** 
- This script uses ChromeCDM 2209
- I'm not responsible for any action caused by the abuse of this script.
- **DO NOT ABUSE THIS SCRIPT!**

## Prerequisites
- `Python3.6` or later
- Add `mp4decrypt`,`mp4dump`,`aria2c` to `$PATH` (CRITICAL)
- Install required packages

  ```
  $ pip install -r requirements.txt
  ```
## Instructions
1. Clone or Download the Repo 
2. Run narrowvine_reborn.py

   ```
   $ python3 narrowvine_reborn.py
   ```
3. Enter `MPD_URL` and `LICENSE_URL` of Widevine Content 
4. Once you are done downloading, the script will extract the keys and decrypt the contents.<br> 
5. Enter `FILENAME` with extension! (ex. `final.mp4`)
6. Your decrypted contents will be merged and saved to /output directory. 

## Input Values
- `MPD_URL` - MPD URL of Widevine Content
- `LICENSE_URL` - LICENSE URL of Widevine Content
- `FILENAME` - Desired File Name of Final Decrypted File *(with extension!)*

## Arguments
```
usage: narrowvine_reborn.py [-h] [-mpd MPD] [-lic LICENSE] [-sd]
                            [-k ADD_HEADER] [-o OUTPUT] [-f FILENAME] [-q]

optional arguments:
  -h, --help            show this help message and exit
  -mpd MPD, --video-link MPD
                        CENC MPD
  -lic LICENSE, --license LICENSE
                        Specify license url
  -sd, --skip-dl        Skip download and only decrypt
  -k ADD_HEADER, --add-header ADD_HEADER
                        Add Custom Header
  -o OUTPUT, --output OUTPUT
  -f FILENAME, --filename FILENAME
  -q, --select-quality
```
- For `--add-header`, enter the header in the following format. (`--add-header "{'KEY':'VALUE'}"`)
- If `-q` is enabled, you can choose which quality to download from the MPD stream
- If you pass `-mpd`,`-lic` directly by the commandline, it will skip the manual input process

## Legal Notice
Educational purposes only. Downloading DRM'ed materials may violate their Terms of Service. DO NOT USE THIS FOR PIRACY.

##
If you enjoyed using the script, a star or a follow will be highly appreciated! 😎

 



