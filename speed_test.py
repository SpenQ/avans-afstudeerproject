import subprocess
import time
import os
# ./rabe-debug --scheme BSW decrypt --public\ key pk.rkey --input $(./rabe-debug --scheme BSW encrypt --input a --policy "{ \"OR\": [ { \"ATT\": \"att01\"}, {\"ATT\": \"test2\"} ] }") --secret\ key secretkey
# ./rabe-debug --scheme BSW keygen --attribute\(s\) att01 > secretkey

# for loop 10 times
    # create pk with n atts
    # create policy of ? attributes
    # start timer
    # encrypt string of 1 char with policy
    # stop timer
    # start timer
    # decrypt string with premade key
    # stop timer
    
atts = ["att1", "att2", "att3"]

cmd="./rabe-debug --scheme BSW keygen --attribute\\(s\\) \"{atts}\"" # TODO convert to C bindings

result = subprocess.check_output(cmd.format(atts = " ".join(atts)), shell=True)
# print(result)
f = open("secret", "w")
f.write(result)
f.close()

cmd="./rabe-debug --scheme BSW encrypt --input aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa --policy \"{ \\\"OR\\\": [ { \\\"ATT\\\": \\\"att5\\\"}, { \\\"AND\\\": [ { \\\"ATT\\\": \\\"att1\\\"}, { \\\"OR\\\": [ { \\\"ATT\\\": \\\"att4\\\"}, {\\\"ATT\\\": \\\"att2\\\"} ] } ] } ] }\""
cyphertext = subprocess.check_output(cmd, shell=True)

cmd="./rabe-debug --scheme BSW decrypt --public\ key pk.rkey --input {cyphertext} --secret\ key secret"
t0 = time.time()
result = subprocess.check_output(cmd.format(cyphertext = cyphertext), shell=True)
t1 = time.time()
print(str(t1-t0))
# print(len(result))