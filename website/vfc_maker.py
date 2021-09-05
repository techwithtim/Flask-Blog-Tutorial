
from os import replace


def make_vfc(info):
    nameforfn = info.name.replace(" ", "").replace(".","").lower()
    splitname = info.name.split()
    last_name = splitname[-1]
    first_name = splitname[int(len(splitname) / 2)]
    title = splitname[0]
    filename = nameforfn + ".vcf"
    with open ("website/"+filename, 'w') as file:
        file.write("BEGIN:VCARD\nVERSION:3.0\nPRODID:-//Apple Inc.//macOS 12.0//EN\n")
        file.write("N:" + last_name + ";" + first_name + ";;" + title + ";\n")
        file.write("FN:" + info.name + "\n")
        file.write("item1.EMAIL;type=INTERNET;type=pref:" + info.email + "\n")
        file.write("ORG:"+info.company+"\n")
        file.write("TEL;type=WORK;type=VOICE;type=pref:" + info.phone + "\n")
        file.write("ADR;type=WORK;type=pref:;;" + info.address + ";" + info.city + ";" + info.state + ";" + info.zip + ";United States\n")
        file.write("END:VCARD")
    return filename

