# WifiSweep
Automated capturing of WPA &amp; WPA2 password Hashes.

When usinig Linux, home folder has special permissions for deleting directories. To avoid inability to delete folders don't open in home directory ie. your username.

to delete files in terminal -> sudo rm -R WifiSweep/session name

Dependencies | hcxdumptool, hashcat

# For wordlist cracking
hashcat -m 22000 -o Solis-pass Solis.hc22000 /usr/share/wordlists/rockyou.txt

#For brute-force cracking
hashcat -m 22000 hash.hc22000 -a 3 ?d?d?d?d?d?d?d?d

# for brute forcing with increments 
hashcat -m 22000 hash.hc22000 -a 3 --increment --increment-min 8 --increment-max 18 ?d?d?d?d?d?d?d?d?d?d?d?d?d?d?d?d?d?d
