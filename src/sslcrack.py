# A simple script for cracking a Schildbach wallet file password encrypted with 
# AES-256 CBC MD5
#
# Author: Josh McIntyre
#
import subprocess
import sys
import os

# Define passwords to try
pws = [ 'foobar', 'foobarbaz' ]

# This runs the OpenSSL command via subprocess.run, which just shells out to run the specified command
# It's a little slower, but it's the simplest way to accomplish this without having to deal with openssl enc's odd behavior
INPUT_FILE = "wallet.txt.enc"
CHECK_CMD = r"cat wallet.txt | tr -cd [:print:] | awk '{print $1}'"

def openssl_attempt(password):

    output_file = "wallet.txt"
    args = [ "openssl", "enc", "-d", "-aes-256-cbc", "-md", "md5", "-a", "-in", INPUT_FILE, "-out", output_file, "-k" ] + [ password ]

    ret = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if ret.returncode == 0:
        try:
            ret_check = os.popen(CHECK_CMD).read().strip()
            if "#" in ret_check or "org.bitcoin.production" in ret_check: 
                with open(output_file) as f:
                    data = f.read()
                    f.seek(0,0)
                    print(f"Possible decryption with password *** {password} ***")
                    print(f"Possible signature of Schildbach wallet, verify by running OpenSSL command line with password {password}.")
                    print("-------------- Wallet file contents --------------")
                    for line in f:
                        print(line.strip())
                    print("-------------- End wallet file contents ------------")
                return True
        except UnicodeDecodeError:
            pass # Normally not good to fail silently - but this case is a false positive decryption

    return False 

# Make sure the wallet file is there
try:
    with open(INPUT_FILE) as f:
        pass
except FileNotFoundError:
    print(f"File {INPUT_FILE} not found. Please rename a copy of wallet file to {INPUT_FILE} and make sure it's in the same folder as this script")
    sys.exit(1)

NUM_PLACEHOLDER = "0-9999"

# Try and crack with the password list first
print(f"Attempting with initial password list")
success_pwlist = False
for pw in pws:
    if not NUM_PLACEHOLDER in pw:
        print(f"Attempting password {pw}")
        ret = openssl_attempt(pw)
        if ret:
            success_pwlist = True

if not success_pwlist:
    print("Unable to decrypt wallet with initial password list. Now trying variants, this may take several hours")

success_variant = False
for pw in pws:
    if NUM_PLACEHOLDER in pw:
        print(f"Attempting numerical variations of password {pw}")
        for num in range(0, 9999):

            # Try numerical substitution
            var = pw.replace(NUM_PLACEHOLDER, str(num))
            ret = openssl_attempt(var)
            if ret:
                success_variant = True

            if ret:
                success_variant = True
            var = pw.replace(NUM_PLACEHOLDER, rom.lower())
            ret = openssl_attempt(var)
            if ret:
                success_variant = True

os.remove("wallet.txt")

if not success_variant:
    print("Unable to decrypt wallet with numerical password variations, etc.")
