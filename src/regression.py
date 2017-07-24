'''
Created on Feb 8, 2017

This is the regression script the langlib project.
It is meant to be run at the top level directory of the repository.
'''

import copy,json
from os import walk
from os.path import exists,splitext
from subprocess import Popen, PIPE
from string import digits
import difflib
import sys

#This is the location of the testfiles and manifest relative to the root directory.
testfiles = "./testfiles/"
manifest_file = "./MANIFEST"

#This dict defines the translation from directory names in the "testfiles" directory to actual rosie pattern
#i.e. csharp -> "cs.<pattern>"
langs = { 
        "java" : "java",
        "c" : "c",
        "cpp" : "cpp",
        "csharp" : "cs",
        "go" : "go",
        "javascript" : "js",
        "ruby" : "rb",
        "r" : "r",
        "bash" : "b",
        "vb" : "vb",
        "python" : "py",
        }

#This array defines the actuals expected to be ran by the script. These are also the expected directory names
#for associated tests under the testfiles/language i.e. each "comments" -> "./testfiles/<language>/comments/
tests = [ 
        "comments",
        "dependencies",
        "functions",
        "classes",
        "structs",
        "strings"
        ]

class HtmlPrinter:
    '''
    This is a simple html printer used to write the  various results table generated 
    by run_tests to an html file.
    '''
    def __init__(self,id):
        '''
        Initializes the printer
        
        id : Numeric id of the test execution (test id).
        '''
        self.ts = id
        self.file=open("./result" + str(self.ts) + ".html", 'w')
        
    def add_table(self,test,html):
        self.file.write("<h1>" + test + "</h1>")
        self.file.write(html)
        
    def close(self):
        self.file.close()

def run_tests():
    '''
    This function iterates through all directories found under ./testfiles/ and executes tests if possible.
    
    The process is as follows:
    
    1. Find directory in ./testfiles/, and verify if it maps to a value in the langs. 
       Continue to step 2 if it does not or move to new directory.
    2. Find a directory in the langs directory found in step 1, and verify if it maps to a test in the tests array.
       Continue to step 3 if it does not or move to a new directory.
    3. Find a file in the test directory found in step 2. 
       If the file is correctly named i.e <pattern name><numeric id>.<valid_extension> then strip the numeric id,
       and and the pattern name. 
    4. Verify that the input file has a corresponding json output file in ./testfiles/<lang>/output/<test>/.
       If it does continue to step 5 otherwise move to a new test file.
    5. Execute the input file and compare the results to the output file. Fail the test if a difference is found,
       and print the diff using HTMLPrinter.
    6. Move to new test file as appropriate and continue.
    '''
    failures = 0
    testCount = 0
    printer = HtmlPrinter(sys.argv[1])
    for test in tests:
        for lang,alias in langs.items():
            base_path = testfiles + lang + "/input/" + test + "/"
            for (dirpath, dirnames, test_files) in walk(base_path):
                for test_file in test_files: 
                    resolved_input = dirpath + test_file 
                    resolved_output = splitext(resolved_input)[0].replace("input","output") + ".json"
                    if not exists(resolved_input): continue
                    if not exists(resolved_output): continue
                    with open(resolved_output, 'rU') as vOut:
                        test_file_name = splitext(test_file)[0]
                        pattern = copy.copy(test_file_name)
                        pattern = pattern.translate(None,digits)
                        proc = Popen('rosie -manifest ' + manifest_file + ' -wholefile -encode json ' + alias + "." + pattern + " " + resolved_input, stdout=PIPE, stderr=PIPE,shell=True)
                        stdout = ''
                        stderr = ''
                        for line in proc.stdout: stdout += line
                        for line in proc.stderr: stderr += line
                        if(stderr != ''): print(stderr)
                        try:
                            json1 = json.loads(vOut.read())
                            json2 = json.loads(stdout)
                            jsonOut1 = json.dumps(json1,indent=2, sort_keys=True)
                            jsonOut2 = json.dumps(json2,indent=2, sort_keys=True)
                            if jsonOut1 != jsonOut2:
                                differ = difflib.HtmlDiff()
                                printer.add_table(lang + " : " + test_file_name, ''.join(differ.make_file(jsonOut1.splitlines(True),jsonOut2.splitlines(True))))
                                failures += 1
                                print("-------------------------------------------------")
                                print (test_file_name + " test failed for " + lang)
                        except ValueError:
                            failures += 1
                            print("-------------------------------------------------")
                            print (test_file_name + " test failed for " + lang)
                    testCount += 1
    print("-------------------------------------------------")
    if(testCount == 1):
        print(str(testCount) + " test ran")
    else:
        print(str(testCount) + " tests ran")
    if(failures == 1):
        print(str(failures) + " test failed")
    else:
        print(str(failures) + " tests failed")
    print("-------------------------------------------------")
    printer.close()
    if(failures > 0): exit(1)
    
            
if __name__ == '__main__':
    run_tests()
