import wave
import json
import os
import argparse

# Function to write frames to the WAV file 
def write_frames(filename, frames, num_channels=1, sample_width=2, frame_rate=44100):
    with wave.open(filename, 'w') as wav_file:
        wav_file.setnchannels(num_channels)
        wav_file.setsampwidth(sample_width)
        wav_file.setframerate(frame_rate)
        wav_file.writeframes(frames)

def encode_file(file_str,code,sample_width):
    '''
    return python string of the file extension, or an empty string
    '''
    dot_loc = file_str[::-1].find('.')
    if dot_loc < 0:
        return ''
    file_extension = file_str[len(file_str) - dot_loc:]
    
    ext_len = len(file_extension) # numbers like 2, 3, not exceeding 50
    if ext_len < 50:
        ext_byte = ext_len.to_bytes(1,'big') # get b'\x03'
    else:
        ext_byte = b'\x00'
        
    encoded_extension = b''
    for char in file_extension: # like, jpg
        # todo: key error if invalid file extension
        # code[char] are a numbers like 11, 21, 90
        encoded_extension += bytes.fromhex(str(code[char])) # like b'\x11'
    encoded_extension += ext_byte # like b'\x11\x21\x22'
    
    # Open the file in binary read mode
    with open(file_str, 'rb') as file:
        # Read the entire file into a byte array
        byte_data = file.read()
    output = byte_data + encoded_extension + sample_width.to_bytes(1,'big')
    extra_byte_num = len(output) % sample_width
    if extra_byte_num != 0:
        output += b'\xff'*extra_byte_num
    return output

def get_key_from_value(d, value):
    return next((key for key, val in d.items() if val == value), None)

def decode_file(file_str,code):
    with open(file_str, 'rb') as file:
        wav_file = wave.open(file, 'rb')
        num_frames = wav_file.getnframes()
        frames = wav_file.readframes(num_frames)
        sample_width = wav_file.getsampwidth()
        wav_file.close()
    for i in range(len(frames)):
        last_byte = frames[-1-i]
        if last_byte < 255:
            break
    if last_byte != sample_width:
        print('wav sample width modified!')
        print('should be',last_byte)
        print('but is',sample_width)
        return None
    else:
        ext_len = frames[-2-i] # like 5
        ext = frames[-2-ext_len-i:-2-i].hex() # like '8183616353'
        ext_values = [int(ext[i:i+2]) for i in range(0, len(ext), 2)] # like [81,83,61,63,53]
        file_extension = ''
        for char in ext_values:
            file_extension += get_key_from_value(code, char) # like ipynb
        with open('output.'+file_extension, 'wb') as file:
            file.write(frames[:-2-ext_len-i])

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="file encoder and decoder to wav")
    parser.add_argument('--mode','-m', choices=['encode', 'decode'],default='encode', help='encode/decode mode')
    parser.add_argument('file',type = str,help='location of file to handle')
    parser.add_argument('--code',default=None,help='code for file extension')
    parser.add_argument('--sample_width',default=2,type=int,help='wav sample width, defult 2')
    
    default_code = {
            'q':11,
            'w':21,
            'e':31,
            'r':41,
            't':51,
            'y':61,
            'u':71,
            'i':81,
            'o':91,
            'a':12,
            's':22,
            'd':32,
            'f':42,
            'g':52,
            'h':62,
            'j':72,
            'k':82,
            'l':92,
            'z':13,
            'x':23,
            'c':33,
            'v':43,
            'b':53,
            'n':63,
            'm':73,
            'p':83,
            '0':93,
            '1':10,
            '2':20,
            '3':30,
            '4':40,
            '5':50,
            '6':60,
            '7':70,
            '8':80,
            '9':90,
    }
    
    args = parser.parse_args()
    
    if args.code is None:
        code = default_code
    else:
        try:
            # load code from json
            with open(args.code, 'r') as json_file:
                code = json.load(json_file)
        except:
            print('code file incorrect, use default')
            code = default_code

    # Parameters for the WAV file
    num_channels = 1  # Mono
    frame_rate = 44100  # 44.1 kHz
    
    # parse file
    normalized_path = os.path.normpath(args.file)
    file_name, file_extension = os.path.splitext(normalized_path)
    
    if args.mode == 'encode':
        file_encoded = encode_file(args.file,code,args.sample_width)
        file_encoded_name = 'WavReMiX_'+file_name[:10]+'.wav'
        write_frames(file_encoded_name, file_encoded, num_channels=num_channels, sample_width=args.sample_width, frame_rate=frame_rate)
    else:
        decode_file(args.file,code)
        


