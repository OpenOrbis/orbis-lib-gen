#!/usr/bin/python
import collections
import sys, os, json, codecs

#print introduction
print('\nPS4 Header and Stub Source Generator\nBy CrazyVoid\n')

header_template_fh = open("data/header.template", "r")
header_template_content = header_template_fh.read()
header_template_fh.close()

source_template_fh = open("data/source.template", "r")
source_template_content = source_template_fh.read()
source_template_fh.close()

# List of json files to ignore when generating stubs.
# These are useless for our sdk, it will make stuff 
# more clean during the final release of OpenOrbis SDK
ignore_jsons = ["custom_video_core.elf.json", 
				"I18N.CJK.dll.sprx.json", 
				"I18N.dll.sprx.json", 
				"I18N.MidEast.dll.sprx.json", 
				"I18N.Other.dll.sprx.json", 
				"I18N.Rare.dll.sprx.json", 
				"I18N.West.dll.sprx.json", 
				"JSC.Net.dll.sprx.json", 
				"libSceNKWeb.sprx.json", 
				"libSceNKWebCdlgInjectedBundle.sprx.json", 
				"libSceNKWebKit.sprx.json", 
				"libSceNKWebKitRequirements.sprx.json", 
				"libSceShellUIUtil.sprx.json", 
				"libSceWebKit2.sprx.json", 
				"libSceWebKit2ForVideoService.sprx.json", 
				"libSceWebKit2Secure.sprx.json", 
				"libswctrl.sprx.json", 
				"libswreset.sprx.json", 
				"LoginMgrUIProcess.self.json",
				"LoginMgrWebProcess.self.json",
				"NKNetworkProcess.self.json",
				"NKUIProcess.self.json",
				"NKWebProcess.self.json",
				"NKWebProcessHeapLimited.self.json",
				"orbis-jsc-compiler.self.json",
				"ReactNative.Components.Vsh.dll.sprx.json",
				"ReactNative.Debug.DevSupport.dll.sprx.json",
				"ReactNative.Modules.Vsh.dll.sprx.json",
				"ReactNative.Modules.Vsh.Gct.Telemetry.dll.sprx.json",
				"ReactNative.Modules.Vsh.Gct.Telemetry2.dll.sprx.json",
				"ReactNative.PUI.dll.sprx.json",
				"ReactNative.Vsh.Common.dll.sprx.json",
				"Sce.Facebook.CSSLayout.dll.sprx.json",
				"ScePlayReady.self.json",
				"ScePlayReady2.self.json",
				"SecureUIProcess.self.json",
				"SecureWebProcess.self.json",
				"swagner.self.json",
				"swreset.self.json",
				"UIProcess.self.json",
				"ulobjmgr.sprx.json",
				"webapp.self.json",
				"WebBrowserUIProcess.self.json",
				"WebProcess.self.json",
				"websocket-sharp.dll.sprx.json"]

rename_jsons = {
	("libkernel", "libkernel_sys"): "libkernel_sys",
	("libSceFreeType", "libSceFreeTypeSubFunc"): "libSceFreeTypeSubFunc",
	("libSceFreeType", "libSceFreeTypeOptOl"): "libSceFreeTypeOptOl",
	("libSceFreeType", "libSceFreeTypeHinter"): "libSceFreeTypeHinter",
}

msCount = 0

# Print Help Function
def printHelp():
	print('Usage : generate.py idc_ps4libdoc_location\n')
	print('ps4libdoc location is the system/common/lib folder\n\n')
	

# Generate Asm Function
def genAsm(symbol_names, xmodule_name):
	prxPrototypeList = list()
	prxFunctionList = list()
	
	global linker_data
	
	fnCount = 0
	
	xheader_filename = (xmodule_name + ".h")
	xsource_filename = (xmodule_name + ".c")
	
	xsource_content_temp = source_template_content
	
	xheader_content_temp = header_template_content
	
	hookedName = xmodule_name[3:]
	fixedName = "lib" + hookedName

	xsource_content_temp = xsource_content_temp.replace("%%header_string%%", xheader_filename)
	
	for prxSyms in symbol_names:
		fnCount += 1
		print(fixedName + " - Symbol Name : " + prxSyms + "\n")
		prxPrototypeList.append("void " + prxSyms + "() { for(;;){} }\n")
		prxFunctionList.append("void " + prxSyms + "();\n")

			
	
	tempPrototypeList = "".join(prxPrototypeList)
	tempFunctionList = "".join(prxFunctionList)
	
	xsource_content_temp = xsource_content_temp.replace("%%PROTOTYPE_LIST%%", tempPrototypeList)
	xheader_content_temp = xheader_content_temp.replace("%%FUNCTION_LIST%%", tempFunctionList)
	
	if fnCount <= 0:
		print('Function count is 0 for this library, no stub or header is needed')
		return

	print("[INFO] Generating " + xmodule_name + " Header\n")
	output_header_fh = open("build/" + xheader_filename, "w")
	output_header_fh.write("".join(xheader_content_temp))
	output_header_fh.close()

	print("[INFO] Generating " + xmodule_name + " Source\n")
	output_source_fh = open("build/" + xsource_filename, "w")
	output_source_fh.write("".join(xsource_content_temp))
	output_source_fh.close()


#Check if there the proper amount of args
if len(sys.argv) != 2:
	printHelp()
	sys.exit(0)
	
# Check if build folder exist, if not create it!
if not os.path.exists('build'):
	os.makedirs('build')
	print('[INFO] Creating Folder Build\n')
else:
	print('[INFO] Build Folder exists\n')

input_idc_file_loc = sys.argv[1]
print("Stub Documentation File Location : " + sys.argv[1] + "\n")

generation_map = collections.defaultdict(set)

for jsonFile in os.listdir(input_idc_file_loc):
	if not jsonFile.endswith(".sprx.json"):
		print("[INFO] " + jsonFile + " Is not a sprx documentation\n")
		continue

	print("[INFO] Loading Sprx Documentation File : " + jsonFile + "\n")

	if jsonFile in ignore_jsons:
		print("[BLOCKED] Json is in blocked json list.\n")
		continue

	input_sprx_content = json.load(codecs.open(input_idc_file_loc + "/" + jsonFile, 'r', 'utf-8-sig'))

	module_name = input_sprx_content["modules"][0]["name"]
	json_name = jsonFile[:-10] # strip .sprx.json

	if (module_name, json_name) in rename_jsons:
		module_name = rename_jsons[(module_name, json_name)]

	print("Module : " + module_name + " - Generating Stub for this prx!\n")

	for modLibrary in input_sprx_content["modules"][0]["libraries"]:

		lib_name = modLibrary["name"]
		lib_is_export = modLibrary["is_export"]
		lib_symbols = modLibrary["symbols"]

		# Rename colliding libs
		if (lib_name, json_name) in rename_jsons:
			lib_name = rename_jsons[(lib_name, json_name)]

		print("[LIBRARY_DETECTED] : " + lib_name + "\n")
		if not lib_is_export:
			print("IS_EXPORT (FALSE) -> No lib for " + lib_name + "\n")
			continue

		symbols = generation_map[lib_name]
		for s in lib_symbols:
			if "name" in s and s["name"] is not None:
				symbols.add(s["name"])

for lib_name, symbols in generation_map.items():
	symbols_list = sorted(symbols)
	print("[GENERATING] " + lib_name + " with " + str(len(symbols_list)) + " symbols\n")
	genAsm(symbols_list, lib_name)

print("[INFO] Finished Generating PRX Source Files\n")
