import sys
import os
import pathlib
import shutil

def index_Multi(List,liter):
	index_L = []
	for val in range(0,len(List)):
		if liter == List[val]:
			index_L.append(val)
	return index_L

def is_use_shell(cmd):
	return cmd == 'deb' or cmd == 'apt' or cmd == 'pge' or cmd == 'run'

if "-f" in sys.argv:
	filesystem = sys.argv[sys.argv.index("-s")+1]
elif "--filesystem" in sys.argv:
	filesystem = sys.argv[sys.argv.index("--squashfs")+1]
else:
	print("{} : squash filesystem file not specified")
	sys.exit(1)

if "-p" in sys.argv:
	plymouththeme = sys.argv[sys.argv.index("-p")+1]
	print("selected plymouth theme {}".format(plymouththeme))
elif "--plymouth" in sys.argv:
	plymouththeme = sys.argv[sys.argv.index("--plymouth")+1]
	print("selected plymouth theme {}".format(plymouththeme))
else:
	plymouththeme = None

if "-s" in sys.argv:
	flow_path = sys.argv[sys.argv.index("-f")+1]
elif "--script" in sys.argv:
	flow_path = sys.argv[sys.argv.index("--flow")+1]
else:
	print("{} : script file not specified")
	sys.exit(1)

flow = []
with open(flow_path) as f:
	beforecmd = None
	l_strip = [s.strip() for s in f.readlines()]
	for s in l_strip:
		cmd = s[:3]
		if cmd == "add":
			args = s[3:].split()
			fromfile = args[0]
			tofile = args[1]
			if os.path.isfile(fromfile):
				pass
			elif os.path.isdir(fromfile):
				pass
			else:
				print("{} : {} : {} :no such file or dirctory.".format(sys.argv[0],flow_path,fromfile))
				sys.exit(1)
			if tofile[0] != "/":
				print("{} : error : {} is not full path.".format(sys.argv[0],tofile))
				sys.exit(1)
			print("copy from {} to ./squashfs-root{}".format(fromfile,tofile))
			flow.append([1,fromfile,tofile])
			del args
			del fromfile
			del tofile
		if cmd == "rmv":
			args = s[3:].split()
			rmfile = args[0]
			if rmfile[0] != "/":
				print("{} : error : {} is not full path.".format(sys.argv[0],rmfile))
				sys.exit(1)
			print("remove {}".format(rmfile))
			flow.append([2,rmfile])
			del args
			del rmfile
		if cmd == "apt":
			args = s[3:].split()
			packname = args[0]
			if is_use_shell(beforecmd):
				flow[len(flow)-1].append([1,packname])
			else:
				flow.append([3,[1,packname]])
			print("install {}".format(packname))
			del args
			del packname
		if cmd == "deb":
			args = s[3:].split()
			debfile = args[0]
			if debfile[-4:] != ".deb":
				print("{} : error : {} is not deb package file.".format(sys.argv[0],debfile))
				sys.exit(1)
			if is_use_shell(beforecmd):
				flow[len(flow)-1].append([2,debfile])
			else:
				flow.append([3,[2,debfile]])
			print("install {}".format(debfile))
			del args
			del debfile
		if cmd == "pge":
			args = s[3:].split()
			purgename = args[0]
			if is_use_shell(beforecmd):
				flow[len(flow)-1].append([3,purgename])
			else:
				flow.append([3,[3,purgename]])
			print("purge {}".format(purgename))
			del args
			del purgename
		if cmd == "run":
			runcommand = s[4:]
			if is_use_shell(beforecmd):
				flow[len(flow)-1].append([4,runcommand])
			else:
				flow.append([3,[4,runcommand]])
			print("run \"{}\"".format(runcommand))
			del runcommand
		beforecmd = s[:3]
del flow_path
del cmd
del beforecmd
print(flow)
print("now unpacking {}".format(filesystem))
os.system("unsquashfs {}".format(filesystem))

del filesystem
with open("./squashfs-root/etc/resolv.conf","w") as f:
	f.write("nameserver 1.1.1.1\n")
	f.write("nameserver 8.8.8.8\n")

with open("./squashfs-root/tmp/runsquashfs.sh","w") as f:
	f.write("#!/bin/bash\n")
	f.write("sudo apt-get update\n")
	f.write("sudo apt-get install -y gdebi\n")
	if plymouththeme != None:
		print("copy {} to ./squashfs-root/usr/share/plymouth/themes/{}".format(plymouththeme,pathlib.Path(plymouththeme).name))
		os.system("cp -r {} ./squashfs-root/usr/share/plymouth/themes/".format(plymouththeme))
		f.write("plymouth-set-default-theme {}\n".format(pathlib.Path(plymouththeme).name))
		f.write("plymouth-set-default-theme {} -R\n".format(pathlib.Path(plymouththeme).name))
		f.write("update-initramfs -u -k all\n")

os.system("sudo chroot squashfs-root/ bash /tmp/runsquashfs.sh")

del plymouththeme

for r in flow:
	print(r)
	if r[0] == 1:
		os.system("cp -r {} ./squashfs-root{}".format(r[1],r[2]))
		print("copy {} to {}".format(r[1],r[2]))
	if r[0] == 2:
		if os.path.exists("./squashfs-root{}".format(r[1])):
			os.system("rm -r ./squashfs-root{}".format(r[1]))
			print("remove {}".format(r[1]))
		else:
			print("{} : {} : no such file or directory".format(sys.argv[0],r[1]))
	if r[0] == 3:
		with open("./squashfs-root/tmp/runsquashfs.sh","w") as f:
			f.write("#!/bin/bash\n")
			r = r[1:]
			for rr in r:
				if rr[0] == 1:
					f.write("sudo apt-get install  -y {}\n".format(rr[1]))
					print("install {}".format(rr[1]))
				if rr[0] == 2:
					os.system("cp {} squashfs-root/tmp/".format(rr[1]))
					print("copy {} to /tmp/".format(rr[1]))
					f.write("yes | sudo gdebi /tmp/{}\n".format(os.path.basename(rr[1])))
					print("install {}".format(rr[1]))
					f.write("rm /tmp/{}\n".format(os.path.basename(rr[1])))
				if rr[0] == 3:
					f.write("sudo apt-get remove -y --purge --autoremove {}\n".format(rr[1]))
					print("purge {}".format(rr[1]))
				if rr[1] == 4:
					f.write("{}\n".format(rr[1]))
					print("run '{}'".format(rr[1]))
		os.system("sudo chroot squashfs-root/ bash /tmp/runsquashfs.sh")

os.system("mksquashfs ./squashfs-root/ filesystem.squashfs -comp xz")
