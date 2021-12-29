#!/bin/bash

print_and_exit() {
    echo "Need to add license header to file $1"
    exit 1
}


files=$(find ./compiler/{include,lib,src} -iregex '^.*\.\(cpp\|cc\|h\|hpp\)$')

for file in $files
do
    cmp <(head -n 4 $file) <(echo "// Part of the Concrete Compiler Project, under the BSD3 License with Zama
// Exceptions. See
// https://github.com/zama-ai/homomorphizer/blob/master/LICENSE.txt for license
// information.") || print_and_exit $file
done

files=$(find ./compiler/{include,lib,src} -iregex '^.*\.\(py\)$')

for file in $files
do
    cmp <(head -n 2 $file) <(echo "#  Part of the Concrete Compiler Project, under the BSD3 License with Zama Exceptions.
#  See https://github.com/zama-ai/homomorphizer/blob/master/LICENSE.txt for license information.") || print_and_exit $file
done
