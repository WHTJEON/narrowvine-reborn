import subprocess, os, argparse, json, time, binascii, base64, requests, sys
from ffmpy import FFmpeg
from pywidevine.decrypt.wvdecrypt import WvDecrypt
import shutil
import glob
import pathlib
import platform
try:
    import readline
except:
    pass

youtubedlexe = 'yt-dlp'
aria2cexe = 'aria2c'
mp4dumpexe = "mp4dump"
mp4decryptexe = "mp4decrypt"

currentFile = __file__
realPath = os.path.realpath(currentFile)
dirPath = os.path.dirname(realPath)
dirName = os.path.basename(dirPath)
cachePath = dirPath+"/cache"
outputPath = dirPath+"/output"
toolsPath = dirPath + '/tools'

parser = argparse.ArgumentParser()
parser.add_argument("-mpd", "--video-link", dest="mpd", help="CENC MPD", required=False,default=None)
parser.add_argument("-lic","--license", help="Specify license url", required=False,default=None)
parser.add_argument("-sd","--skip-dl",action ="store_true",help="Skip download and only decrypt",default=False)
parser.add_argument("-k","--add-header",help="Add Custom Header",required=False,default=None)
parser.add_argument("-o","--output",default=outputPath)
parser.add_argument("-f","--filename",default=None)
parser.add_argument("-q","--select-quality",action="store_true",default=False)
args = parser.parse_args()

mpd_link_args = args.mpd
license_url_args = args.license
header_args = args.add_header
filename_args = args.filename
select_quality_yn = args.select_quality
outputPath = args.output
skip_download = args.skip_dl

FInput_video = dirPath + '/cache/encrypted_video.mp4'
FInput_audio = dirPath + '/cache/encrypted_audio.m4a'
out_Audio = FInput_audio.replace('encrypted', 'decrypted')
out_Video = FInput_video.replace('encrypted', 'decrypted')

def divider():
    count = int(shutil.get_terminal_size().columns)
    count = count - 1
    print ('-' * count)
    
def empty_folder(folder):
    files = glob.glob('%s/*'%folder)
    for f in files:
        os.remove(f)
    
def download_drm_content(mpd_url):    
    if select_quality_yn == True:
        divider()
        print("[info] Processing Video Info..")
        os.system('yt-dlp --external-downloader aria2c --no-warnings --allow-unplayable-formats --no-check-certificate -F "%s"'%mpd_url)
        divider()
        VIDEO_ID = input("ENTER VIDEO_ID (Press Enter for Best): ")
        if VIDEO_ID == "":
            VIDEO_ID = "bv"
            
        AUDIO_ID = input("ENTER AUDIO_ID (Press Enter for Best): ")
        if AUDIO_ID == "":
            AUDIO_ID = "ba"
    else:
        VIDEO_ID = "bv"
        AUDIO_ID = "ba"
        
    divider()
    print("[info] Downloading Encrypted Video from CDN..")	
    os.system(f'yt-dlp -o "{cachePath}/encrypted_video.%(ext)s" --no-warnings --external-downloader aria2c --allow-unplayable-formats --no-check-certificate -f {VIDEO_ID} "{mpd_url}" -o "{cachePath}/encrypted_video.%(ext)s"')
    print("[info] Downloading Encrypted Audio from CDN..")
    os.system(f'yt-dlp -o "{cachePath}/encrypted_audio.m4a" --no-warnings --external-downloader aria2c --allow-unplayable-formats --no-check-certificate -f {AUDIO_ID} "{mpd_url}"')
    
def merge_content():
    if filename_args == None:
        divider()
        FILENAME=input("Enter File Name (with extension): \n> ")
    else:
        FILENAME = filename_args
    divider()
    print("[info] Merging Files and Processing %s.. (Takes a while)"%FILENAME)
    ff = FFmpeg(
        global_options=['-loglevel','error'],
        outputs={f'{outputPath}/{FILENAME}': ['-c:v','copy','-c:a','copy']},
        inputs={
            f'{cachePath}/decrypted_video.mp4':None,
            f'{cachePath}/decrypted_audio.m4a':None}
    )		
    ff.run()

def get_kid():
    global KID_video
    KID = ''
    pssh = None
    def find_str(s, char):
            index = 0
            if char in s:
                c = char[0]
                for ch in s:
                    if ch == c and s[index:index + len(char)] == char:
                        return index
                    index += 1
                    
            return -1
    
    mp4dump = subprocess.Popen([mp4dumpexe, FInput_audio], stdout=subprocess.PIPE)
    mp4dump = str(mp4dump.stdout.read())
    A = find_str(mp4dump, 'default_KID')
    KID = mp4dump[A:A + 63].replace('default_KID = ', '').replace('[', '').replace(']', '').replace(' ', '')
    KID = KID.upper()
    KID_video = KID[0:8] + '-' + KID[8:12] + '-' + KID[12:16] + '-' + KID[16:20] + '-' + KID[20:32]
    
    if KID == '':
        KID = 'nothing'
    return KID_video

def Get_PSSH(mp4_file):
    global mp4dumpexe
    currentFile = __file__
    realPath = os.path.realpath(currentFile)
    dirPath = os.path.dirname(realPath)
    dirName = os.path.basename(dirPath)
    WV_SYSTEM_ID = '[ed ef 8b a9 79 d6 4a ce a3 c8 27 dc d5 1d 21 ed]'
    pssh = None
    data = subprocess.check_output(['mp4dump', '--format', 'json', '--verbosity', '1', mp4_file])
    data = json.loads(data)
    for atom in data:
        if atom['name'] == 'moov':
            for child in atom['children']:
                if child['name'] == 'pssh' and child['system_id'] == WV_SYSTEM_ID:
                    pssh = child['data'][1:-1].replace(' ', '')
                    pssh = binascii.unhexlify(pssh)
                    #if pssh.startswith('\x08\x01'):
                    #   pssh = pssh[0:]
                    pssh = pssh[0:]
                    pssh = base64.b64encode(pssh).decode('utf-8')
                    return pssh
    
def get_pssh(keyId):
    array_of_bytes = bytearray(b'\x00\x00\x002pssh\x00\x00\x00\x00')
    array_of_bytes.extend(bytes.fromhex('edef8ba979d64acea3c827dcd51d21ed'))
    array_of_bytes.extend(b'\x00\x00\x00\x12\x12\x10')
    array_of_bytes.extend(bytes.fromhex(keyId.replace('-', '')))
    return base64.b64encode(bytes.fromhex(array_of_bytes.hex()))

def createpsshfromkid(kid):
    kid = kid.replace('-', '')
    if len(kid) == 32 and isinstance(kid, bytes):
        raise AssertionError('Wrong KID length')
    return get_pssh(kid).decode('utf-8')

def do_decrypt(kid, licurl,headers):
    pssh = createpsshfromkid(kid)
    wvdecrypt = WvDecrypt(pssh)
    chal = wvdecrypt.get_challenge()
    resp = requests.post(url=licurl, data=chal, headers=headers)
    license_decoded = resp.content
    license_b64 = base64.b64encode(license_decoded)
    wvdecrypt.update_license(license_b64)
    keys = wvdecrypt.start_process()
    print("[info] Found Key!")
    return keys

def keysOnly(keys):
    for key in keys:
        if key.type == 'CONTENT':
            key = ('{}:{}'.format(key.kid.hex(), key.key.hex()))            
    return key

def proper(keys):
    commandline = [mp4decryptexe]
    for key in keys:
        if key.type == 'CONTENT':
            commandline.append('--key')
            commandline.append('{}:{}'.format(key.kid.hex(), key.key.hex()))
            
    return commandline

def decrypt(keys_, inputt, output):
    Commmand = proper(keys_)
    Commmand.append(inputt)
    Commmand.append(output)
    wvdecrypt_process = subprocess.Popen(Commmand)
    stdoutdata, stderrdata = wvdecrypt_process.communicate()
    wvdecrypt_process.wait()
    
#INIT
divider()
#empty_folder(cachePath)
print("**** NARROWVINE-REBORN by vank0n ****")
divider()

if mpd_link_args == None and license_url_args == None and header_args == None:
    if skip_download == False:
        MPD_URL = input("Enter MPD URL: \n> ")
        divider()
        licurl = input("Enter License URL: \n> ")
        if header_args != None:
            divider()
            headers = input("Enter Custom Header: \n> ")
        download_drm_content(MPD_URL)
    else:
        licurl = input("Enter License URL: \n> ")
        if header_args != None:
            divider()
            headers = input("Enter Custom Header: \n> ")
        divider()
        print("[info] Skipping Download")
        
    divider()
else:
    print("[info] Entering Download Section")
    MPD_URL = mpd_link_args
    licurl = license_url_args
    if skip_download == False:
        download_drm_content(MPD_URL)
    
print('[info] Attempting Widevine challenge...')
print('[info] Getting Keys...')

if header_args == None:
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.75 Safari/537.36' 
    }
else:
    headers = eval(header_args)
    
KEYS = do_decrypt(licurl=licurl, kid=get_kid(),headers=headers)

try:
    if not os.path.exists(out_Video):
        print ("[info] Decrypting Video Using KEY: " + keysOnly(KEYS))
        command = decrypt(KEYS, FInput_video, out_Video)
except Exception:
    pass

if not os.path.exists(out_Audio):
    print ("[info] Decrypting Audio Using KEY: " + keysOnly(KEYS))
    command = decrypt(KEYS, FInput_audio, out_Audio)
    
merge_content()
divider()
print("[info] Process Finished. Final Video File is saved in %s"%outputPath)
divider()
delete_choice = input("Delete cache files? (y/n)\ny) Yes (default)\nn) No\ny/n> ")
if delete_choice == "n":
    pass
else:
    empty_folder(cachePath)
    
divider()
print("[info] Emptied Temporary Files")
print("[info] Process Complete")
divider()
quit()
