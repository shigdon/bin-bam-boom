perl -ne 'm/^>(\S+)/ and print("$1\t1\n")' < CAR_10.1.fa >> CAR_10.1_map.txt
