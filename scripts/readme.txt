
# ALSO SEE README.TXT
#
# Process for unpacking the original html file from ElegantOTA library, contained in elegantWebpage.h
# 
#   1. copy out the comma separated data only into a new file and reformat to have one integer per row, without commas.
#   2. use function convert_encoded_gzipped_html_integer_file_into_unzipped_html to unpack the html file
# 	3. Copy and paste out the HTML into https://beautifier.io/ and format the HTML
# 	4. Copy out the long javascript lines and paste into same prettifier and format for javascript
# 	5. Copy back the formatted javascript into the formatted html file
# 	
# Place in HTML file where Device ID is checked for containing case insensitive -IO
# 
# 	1. Search for MBJ around line 4390.
# 	2. If -IO is present in device id, code will prevent upload of binary firmware if filename does not include the device id.
# 	3. If -IO is absent any binary can be uploaded.
# 	
# Place in HTML where SVG file is encoded:
# 
# 	1. Search for data:image/svg+xml;base64,
# 
# To unpack base64 svg string, copy into a text file and use function convert_base64_to_svg
# 
# To pack svg into base64, use function convert_base64_to_svg.
# 
# The svg must not reference a font, any text needs to be converted using Object Menu, Convert to Path in Inkscape
# 
# Once a new HTML file has been written, substitute any updated SVG file in base64 and run function convert_html_to_header