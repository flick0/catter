import json
import argparse
import subprocess

parser = argparse.ArgumentParser(description="Catter")

parser.add_argument("-f","--flavour",help="flavour",type=str,default="mocha")

args = parser.parse_args()


theme = args.flavour

def fill_vars(conf):
    print("filling variables")
    vars = {
        "{CAT::THEME}":theme,
    }
    for var in vars:
        conf = conf.replace(var,vars[var])
    return conf

with open("./example.cat","r") as f:
    dat = json.loads(fill_vars(f.read()))

user = subprocess.run("whoami",stdout=subprocess.PIPE,stderr=subprocess.PIPE).stdout.decode("utf-8").strip()


def get_repo():
    print("cloning repo")
    subprocess.run("cd /tmp/ && mkdir catter",stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True)
    subprocess.run(f"cd /tmp/catter && git clone {dat['source']}",stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True)
    folder = dat["source"].split("/")[-1]
    print("cloned repo")
    return folder

def gen_cat_block(conf:str,comment:str):
    print("generating cat block")
    return f"""{comment*10}CATTER CONFIGURATION{comment*10}
    {conf}
    {comment*10}END CATTER CONFIGURATION{comment*10}"""

def clean_cat_block(conf:str,comment:str):
    print("erasing previous cat block")
    old_conf = conf.split(f"{comment*10}CATTER CONFIGURATION{comment*10}")[-1].split(f"{comment*10}END CATTER CONFIGURATION{comment*10}")[0]
    return conf.replace(f"""{comment*10}CATTER CONFIGURATION{comment*10}
    {old_conf}
    {comment*10}END CATTER CONFIGURATION{comment*10}""","")





folder = get_repo()

out = {
    "all":'',
    "latte":'',
    "frappe":'',
    "macchiato":'',
    "mocha":'',
    "suffix":'',
    "prefix":''
}

for file in dat["use"]:
    print(f"opening file {file}")
    with open(f"/tmp/catter/{folder}/{file}","r") as f:
        conf = f.read()
        if dat["use"][file].get("use_all"):
            out["all"] += "\n" + conf
    if dat["use"][file].get("suffix"):
        out["all"] += "\n" + dat["use"][file]["suffix"]["data"]
        
dest = dat["destination"].replace("~",f"/home/{user}").replace("$HOME",f"/home/{user}")

print("ensuring destination folder exists")
prev = ""
for i in [l for l in dest.split("/")[:-1] if l]:
    prev += "/" + i
    print(prev)
    subprocess.run("mkdir "+prev,stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True)
subprocess.run("touch "+dest,stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True)


with open(dest,"w+") as f:

    if dat["apply"]["append"]:
        before = f.read()
        if dat["apply"]["clean_before_append"]:
            before = clean_cat_block(before,dat["comment_char"])
        before += "\n" + gen_cat_block(out["all"],dat["comment_char"])
        f.write(before)
    else:
        f.write(gen_cat_block(out["all"],dat["comment_char"]))


