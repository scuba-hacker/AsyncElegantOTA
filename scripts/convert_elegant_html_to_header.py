import csv 
import os
import sys
import subprocess
import base64
import struct

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


integers_per_line = 40

def convert_encoded_gzipped_html_integer_file_into_unzipped_html(input_file_path):	

    with open(input_file_path, 'r') as ints:
        integers = [int(line.strip()) for line in ints]
        
        
    # Convert the list of integers to bytes
    binary_data = struct.pack(f"{len(integers)}B", *integers)

    
    # Write the bytes to a binary file
    with open(input_file_path+'.html.gz', 'wb') as gz_file:
        gz_file.write(binary_data)

    command = f"gzip","-d", input_file_path+'.html.gz'

    result = subprocess.run(command)

def read_bytes_file(input_file_path):
    with open(input_file_path, 'rb') as binary_file:
        # Read the entire content of the binary file into a bytes object
        binary_data = binary_file.read()
    return binary_data

def write_bytes_to_csv_multiple_lines(output_file_path, binary_data, items_per_line=integers_per_line):
    # Convert the bytes to a list of integers
    integers = list(binary_data)

    # Create chunks of 'items_per_line'
    chunks = [integers[i:i + items_per_line] for i in range(0, len(integers), items_per_line)]

    # Write chunks to a CSV file with a comma at the end of each line
    with open(output_file_path, 'a', newline='') as csv_file:
        csv_writer = csv.writer(csv_file)
#        csv_writer.writerow(['Bytes'])
        first_line = True
        for chunk in chunks:
            if not first_line:
                csv_file.write(",")
            else:
                first_line = False;
            csv_writer.writerow([*chunk])

def convert_svg_to_base64(device_name):
    input = "elegant_"+device_name+".svg"
    output = "elegant_"+device_name+".txt"
    with open(input,'rb') as svg:
	    svg_bytes = base64.b64encode(svg.read())

    with open(output, 'wb') as svg:
        svg.write('''data:image/svg+xml;base64,'''.encode())
        svg.write(svg_bytes)

def convert_base64_to_svg(svg_base64):
    binary_data = base64.b64decode(svg_base64)
    with open("decoded.svg",'wb') as svg:
        svg.write(binary_data)

def convert_html_to_header(stem, device_label):
    original_html = stem+'.html'
    input_file_path = stem+'.html.gz'
    output_csv_path = "ElegantHTML"+device_label+".h"

    command = f"gzip","--keep", "-f", original_html

    result = subprocess.run(command)

    binary_data = read_bytes_file(input_file_path)

    out_file = open(output_csv_path, mode='w')
    definition = "ElegantHTML"+device_label+"_h"
    out_file.write(
'''#ifndef ''' + definition + '''
#define ''' + definition + '''

const uint32_t ELEGANT_HTML_SIZE = ''')

    out_file.write(str(sys.getsizeof(binary_data)))


    out_file.write(
''';
const uint8_t ELEGANT_HTML[] PROGMEM = { 
''')

    out_file.close()

    write_bytes_to_csv_multiple_lines(output_csv_path, binary_data, items_per_line=integers_per_line)

    out_file = open(output_csv_path, mode='a')
    out_file.write("};\n\n#endif")
    out_file.close()

# convert_encoded_gzipped_html_integer_file_into_unzipped_html("integers.txt")


convert_html_to_header('elegant_new_reef','Reef')
# convert_html_to_header('elegant_new_mako','Mako')
# convert_html_to_header('elegant_new_tiger','Tiger')
# convert_html_to_header('elegant_new_lemon','Lemon')
# convert_html_to_header('elegant_new_silky','Silky')
# convert_html_to_header('elegant_new_oceanic','Oceanic')
# convert_html_to_header('elegant_new_original','Original')


# elegant_ota_original_svg = "PD94bWwgdmVyc2lvbj0iMS4wIiBlbmNvZGluZz0idXRmLTgiPz4KPHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHhtbG5zOnhsaW5rPSJodHRwOi8vd3d3LnczLm9yZy8xOTk5L3hsaW5rIiB2ZXJzaW9uPSIxLjEiIGlkPSJMYXllcl8xIiB4PSIwcHgiIHk9IjBweCIgdmlld0JveD0iMCAwIDI1NCA4MyIgc3R5bGU9ImVuYWJsZS1iYWNrZ3JvdW5kOm5ldyAwIDAgMjU0IDgzOyI+CjxzdHlsZSB0eXBlPSJ0ZXh0L2NzcyI+Cgkuc3Qwe2ZpbGw6IzJFMzAzNDt9Cgkuc3Qxe2ZpbGw6IzQ4OEVGRjt9Cjwvc3R5bGU+CjxnIGlkPSJfeDMwX2I3NDI0NjctMjdlYS1hZTNmLTdjZmEtY2EwZTEwYWMwNGU3IiB0cmFuc2Zvcm09Im1hdHJpeCgyLjIsMCwwLDIuMiwxMDMuODg3NjQxNjY4MzE5NywxMzIuMzU1OTk2MDM2NTI5NTUpIj4KCTxwYXRoIGNsYXNzPSJzdDAiIGQ9Ik0tNi4xLTQ1LjR2LTFILTEzdjkuM2g2Ljh2LTFoLTUuOHYtMy4xaDUuMnYtMWgtNS4ydi0zLjFILTYuMXogTS0zLjYtNDdoLTEuMXY5LjhoMS4xVi00N3ogTTEuMy0zOCAgIGMtMS40LDAtMi4zLTEtMi41LTIuMmg1Ljl2LTAuNGMwLTItMS4zLTMuNi0zLjUtMy42cy0zLjUsMS42LTMuNSwzLjZTLTAuOC0zNywxLjMtMzdDMy0zNyw0LTM3LjksNC41LTM5LjJIMy4zICAgQzMtMzguNSwyLjMtMzgsMS4zLTM4eiBNMS4yLTQzLjNjMS4zLDAsMi4yLDAuOSwyLjQsMi4xaC00LjhDLTAuOS00Mi40LTAuMS00My4zLDEuMi00My4zeiBNMTEuNS00NC4ydjEuMSAgIGMtMC41LTAuOC0xLjMtMS4yLTIuNS0xLjJjLTIsMC0zLjQsMS42LTMuNCwzLjZjMCwyLDEuMywzLjYsMy40LDMuNmMxLjIsMCwyLTAuNSwyLjUtMS4zdjFjMCwxLjQtMC43LDIuMi0yLjMsMi4yICAgYy0xLjEsMC0xLjgtMC40LTItMS4xSDUuOWMwLjQsMS4yLDEuNSwyLDMuMywyYzIuMSwwLDMuMy0xLjEsMy4zLTMuMXYtNi44SDExLjV6IE05LjEtMzguMWMtMS42LDAtMi41LTEuMi0yLjUtMi42ICAgYzAtMS40LDAuOS0yLjYsMi41LTIuNmMxLjUsMCwyLjQsMS4yLDIuNCwyLjZDMTEuNS0zOS4zLDEwLjYtMzguMSw5LjEtMzguMXogTTE3LjMtNDQuM2MtMiwwLTMuNCwxLjYtMy40LDMuNnMxLjMsMy42LDMuNCwzLjYgICBjMS4yLDAsMi0wLjUsMi41LTEuMnYxLjFoMXYtN2gtMXYxLjFDMTkuMy00My44LDE4LjQtNDQuMywxNy4zLTQ0LjN6IE0xNy40LTM4Yy0xLjYsMC0yLjUtMS4yLTIuNS0yLjdjMC0xLjQsMC45LTIuNywyLjUtMi43ICAgYzEuNiwwLDIuNCwxLjIsMi40LDIuN0MxOS44LTM5LjIsMTktMzgsMTcuNC0zOHogTTIyLjctNDQuMnY3aDF2LTRjMC0xLjMsMS0yLjEsMi4xLTIuMWMxLjIsMCwyLDAuOCwyLDIuMXY0aDF2LTQuMSAgIGMwLTItMS4zLTMtMi44LTNjLTEuMSwwLTEuOCwwLjUtMi4zLDEuMnYtMS4xSDIyLjd6IE0zMi4yLTM3LjJ2LTYuMWgxLjZ2LTAuOWgtMS42di0yLjVoLTEuMXYyLjVoLTEuNHYwLjloMS40djYuMUgzMi4yeiAgICBNMzkuMy00Ni41Yy0yLjgsMC00LjcsMi4xLTQuNyw0LjhjMCwyLjYsMS45LDQuNyw0LjcsNC43czQuNy0yLjEsNC43LTQuN0M0NC00NC40LDQyLjEtNDYuNSwzOS4zLTQ2LjV6IE0zOS4zLTM4LjEgICBjLTIuMywwLTMuNy0xLjYtMy43LTMuN2MwLTIuMSwxLjQtMy43LDMuNy0zLjdzMy43LDEuNiwzLjcsMy43QzQzLTM5LjcsNDEuNi0zOC4xLDM5LjMtMzguMXogTTUxLjktNDYuNGgtNy41djFoMy4ydjguM2gxdi04LjMgICBoMy4yVi00Ni40eiBNNTYuNS00Ni40aC0xLjNsLTMuOSw5LjNoMS4ybDEuMS0yLjdoNC42bDEuMSwyLjdoMS4yTDU2LjUtNDYuNHogTTU0LTQwLjhsMS45LTQuNWwxLjksNC41SDU0eiIvPgo8L2c+CjxnIGlkPSJkYzY4OGQxZi1hMDY2LWI3ZTctOGFiYy0xMTVmYTQwZTk0NDUiIHRyYW5zZm9ybT0ibWF0cml4KDAuMjI1NTIwNTc0ODgyOTcxMTEsMCwwLDAuMjI1NTIwNTc0ODgyOTcxMTEsMzQuNTIyNzQzOTgxNjY2ODU2LDExNy4wMTc3NDQ5NjcyNzM1KSI+Cgk8cGF0aCBjbGFzcz0ic3QxIiBkPSJNMTE5LTM0Ny42YzUuNywwLDcuOCw2LjYsNC41LDEwLjhjLTcuMiw4LjQtMTQuNCwxNi41LTIxLjYsMjQuOWMtMi4xLDIuNC02LjYsMi40LTksMCAgIGMtNy4yLTguNC0xNC40LTE2LjUtMjEuNi0yNC45Yy00LjUtNS4xLDEuMi0xMi4zLDYuMy0xMC44aDEzLjJjLTcuMi0yOC44LTI5LjEtNTIuNS01OC44LTU5LjFjLTUuNy0xLjItMTEuNC0xLjgtMTcuMS0xLjggICBjLTI4LjgsMC01NS41LDE1LjktNjkuNiw0MmMtMy45LDcuMi0xNC43LDAuOS0xMC44LTYuM2MxOS4yLTM0LjgsNTkuNC01NC45LDk4LjctNDYuMmMzNS40LDcuNSw2MywzNiw3MC4yLDcxLjQgICBDMTAzLjQtMzQ3LjYsMTE5LTM0Ny42LDExOS0zNDcuNnogTS04My4yLTMwOS4yYy01LjcsMC03LjgtNi42LTQuNS0xMC44YzcuMi04LjQsMTQuNC0xNi41LDIxLjYtMjQuOWMyLjEtMi40LDYuNi0yLjQsOSwwICAgYzcuMiw4LjQsMTQuNCwxNi41LDIxLjYsMjQuOWM0LjUsNS4xLTEuMiwxMi4zLTYuMywxMC44SC01NWM3LjIsMjguOCwyOS4xLDUyLjUsNTguOCw1OS4xYzUuNywxLjIsMTEuNCwxLjgsMTcuMSwxLjggICBjMjguOCwwLDU1LjUtMTUuOSw2OS42LTQyYzMuOS03LjIsMTQuNy0wLjksMTAuOCw2LjNjLTE5LjIsMzUuMS01OS40LDU1LjItOTguNyw0Ni41Yy0zNS40LTcuOC02My4zLTM2LjMtNzAuNS03MS43SC04My4yeiIvPgo8L2c+Cjwvc3ZnPgo="

# convert_base64_to_svg(elegant_ota_original_svg)

# convert_svg_to_base64('reef')
# convert_svg_to_base64('oceanic')
# convert_svg_to_base64('silky')
# convert_svg_to_base64('lemon')
# convert_svg_to_base64('mako')
# convert_svg_to_base64('tiger')

	
