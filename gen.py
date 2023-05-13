import math
import random
import string
import subprocess
import time
import struct

population_size = 100
mutation_rate = 0.09
fitnessScoringType = False # true for
targetValueMax = 5


def create_ppm_from_rgb_string(rgb_string, cols, rows, range_val, output_file_name):
    # Check if the length of the string is valid for the given cols and rows values
    if len(rgb_string) != 3* cols * rows:
        print(len(rgb_string))
        print(cols * rows)
        print(rgb_string)
        raise ValueError('Invalid string length for given cols and rows values')
        
    # Check if the range value is valid
    if range_val < 0 or range_val > 255:
        raise ValueError('Invalid range value')
    
    # Create the PPM header string
    ppm_header = f'P6\n{cols} {rows}\n{range_val}\n'
    
    # Create the binary data string
    binary_data = b''
    for i in range(0, len(rgb_string), 3):
        r, g, b = rgb_string[i], rgb_string[i+1], rgb_string[i+2]
        binary_data += struct.pack('BBB', int(r), int(g), int(b))
    
    # Write the PPM file
    with open(output_file_name, 'wb') as f:
        f.write(ppm_header.encode())
        f.write(binary_data)


def pnmremap(pnm_file,prequant_pnm_file):
    subprocess.run(f"pnmremap -map=websafe.pam {prequant_pnm_file} >{pnm_file}", shell=True)

def createPalette():
    subprocess.run(f"pamseq 3 5 >websafe.pam",shell=True)

createPalette()

def read_ppm(pnm_file):
    # Read the width, height, depth, and maxval from the P7 header
    with open(pnm_file, "rb") as f:
        # Read the first four lines (P7 header) and parse the width, height, depth, and maxval
        magic_number = f.readline().strip()
        header_info = {}
        while True:
            line = f.readline().decode().strip()
            if line.startswith('#'):
                continue
            elif line == '':
                continue
            elif line == 'ENDHDR':
                break
            else:
                key, value = line.split(' ', 1)
                header_info[key] = value

        width = int(header_info['WIDTH'])
        height = int(header_info['HEIGHT'])
        depth = int(header_info['DEPTH'])
        maxval = int(header_info['MAXVAL'])
        
        # Read the remaining lines and convert the pixel values to a string of numbers
        pixel_values = ""
        if depth == 3:
            # RGB image
            for _ in range(height):
                for _ in range(width):
                    pixel = f.read(3)
                    red, green, blue = pixel
                    pixel_values += str(int(targetValueMax*red//maxval))
                    pixel_values += str(int(targetValueMax*green//maxval))
                    pixel_values += str(int(targetValueMax*blue//maxval))
                
        elif depth == 1:
            # Grayscale image
            for _ in range(height):
                for _ in range(width):
                    pixel = f.read(1)
                    gray = pixel[0]
                    pixel_values += str(int(targetValueMax*gray//maxval))
                

    # Construct the output dictionary
    output_dict = {
        "pixel_values": pixel_values,
        "rows": height,
        "columns": width
    }
    
    # Check if the length of the string is valid for the given cols and rows values
    if len(pixel_values.replace('\n', '')) != 3 * width * height:
        print(height)
        print(width)
        print(3 * width * height)
        print(pixel_values.replace('\n', ''))
        raise ValueError('Invalid string length for given width and height values')
        
    return output_dict


def png_to_string(png_file):
    # Define the output file name
    prequant_pnm_file = "pq_output.pnm"
    ppm_file = "output.pnm"

    # Convert the PNG file to a PGM file using the netpbm tools
    subprocess.run(f"pngtopnm {png_file} > {prequant_pnm_file}", shell=True)
    pnmremap(ppm_file, prequant_pnm_file)
    output_dict = read_ppm(ppm_file)
    return output_dict


if __name__ == "__main__":
    # Prompt the user for the input filename
    input_name = input("Enter the input filename (with .png extension): ")

    # Call the png_to_string function with the input file
    output_dict = png_to_string(input_name)

target = output_dict["pixel_values"]
rows = output_dict["rows"]
columns = output_dict["columns"]
if(fitnessScoringType):
    scoreDenominator = len(target)
else:
    scoreDenominator = len(target)*targetValueMax

population = []

def defineRange(max):
    rangeString = ''
    for i in range(0, max +1):
        rangeString += str(i)
    return rangeString

choicePool = defineRange(targetValueMax)

def createPop():

    for i in range(0, population_size):
        population.append((''.join(random.choice(choicePool) for _ in range(len(target))), 0))

    calcFitness(fitnessScoringType)

def createNewPop():
    matingPool = []
    for item in population:
        for i in range(item[1]):
            matingPool.append(item)
    if  len(matingPool) ==0:
        matingPool = population

    population.clear()

    for i in range(population_size):
        parent1 = matingPool[random.randint(0, len(matingPool)-1)]
        parent2 = matingPool[random.randint(0, len(matingPool)-1)]
        evolvedPhrase = mutate(crossover(parent1[0], parent2[0]))
        child = (evolvedPhrase,0)
        population.append(child)
    
    calcFitness(fitnessScoringType)

def calcFitness(absolute):
    global population
    for j in range(len(population)):
        score = 0
        for i in range(len(target)):
            if(absolute):
                if target[i] == population[j][0][i]:
                    score += 1
            else:
                score += targetValueMax - abs(int(target[i]) - int(population[j][0][i]))
        population[j] = (population[j][0], math.floor(100*(score/scoreDenominator)))

    population = sorted(population, key=lambda x: x[1], reverse=True)


def crossover(parent1:str, parent2:str):
    result = ""
    for i in range(len(target)):
        if i % 2 == 0:
            result += parent1[i]
        else:
            result += parent2[i]
    return result

def mutate(phrase:str):
    p = list(phrase)
    for i in range(len(phrase)):
        if random.uniform(0, 1) < mutation_rate:
            if p[i] != target[i]:
                p[i] = random.choice(choicePool)
    return "".join(p)


def string_to_gif(input_string, suffix, columns, rows, pixel_range):
    # Define the input string and file names
    pnm_file = "output_"+suffix+".ppm"
    gif_file = "output_"+suffix+".gif"

    # Write the input string to a PPM file in P6 format
    create_ppm_from_rgb_string(input_string, columns, rows, pixel_range, pnm_file)
    # Convert the PPM file to a GIF file using the netpbm tools
    subprocess.run(f"ppmtogif {pnm_file} > {gif_file}", shell=True)

def bindGifs(lastGeneration, delay, input_files):
    
    gif_files = " ".join(input_files)
    output_file = "result.gif"
    # Combine the input files using gifsicle
    subprocess.run(f"gifsicle --delay={delay} --loopcount=0 {gif_files} > {output_file}", shell=True)

input_files = []

createPop()
generations = 0
while True:
    createNewPop()
    print("Generation: "+ str(generations) +"   -  Progress: " + str(population[0][1]))
    if(generations%10 == 0):
        string_to_gif(population[0][0],str(generations),columns,rows,targetValueMax)
        file_name = "output_" + str(generations) + ".gif"
        input_files.append(file_name)
    generations += 1
    if  population[0][1] == 100 :
        string_to_gif(population[0][0],str(generations),columns,rows,targetValueMax)
        file_name = "output_" +  str(generations) + ".gif"
        input_files.append(file_name)
        print("Number of generations: " + str(generations))
        break
time.sleep(1)
bindGifs(generations,10,input_files)