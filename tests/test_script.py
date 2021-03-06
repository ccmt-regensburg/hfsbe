import os
import glob
import argparse
import numpy as np
import shutil
import sbe.plotting as splt

####################################################################################################
#THIS SCRIPT NEEDS TO BE EXECUTED IN THE MAIN GIT DIRECTORY BY CALLING python3 tests/test_script.py#
####################################################################################################

def check_test(testdir):

    print('\n\n=====================================================\n\nStart with test:'
          '\n\n' + testdir + '\n\n')

    threshold_rel_error = 0.1

    filename_params  = testdir + '/params.py'
    filename_run     = testdir + '/runscript.py'

    for filename in os.listdir(testdir):
        if filename.startswith('reference_Iapprox'):
            filename_Iapprox         = testdir + '/' + filename
        if filename.startswith('reference_Iexact'):
            filename_Iexact         = testdir + '/' + filename
        if filename.startswith('Iexact'):
            filename_Iexact_printed = testdir + '/' + filename

    assert os.path.isfile(filename_params),  'params.py is missing.'
    assert os.path.isfile(filename_run),     'runscript.py is missing.'
    assert os.path.isfile(filename_Iexact),  'Iexact is missing.'
    assert os.path.isfile(filename_Iapprox), 'Iapprox is missing.'

    os.chdir(testdir)

    os.system('python3 runscript.py')

    for filename in os.listdir(testdir):
        if filename.startswith('Iapprox'):
            filename_Iapprox_printed = testdir + '/' + filename
        if filename.startswith('Iexact'):
            filename_Iexact_printed = testdir + '/' + filename

    assert os.path.isfile(filename_Iexact_printed),  "Iexact is not printed from the code"
    assert os.path.isfile(filename_Iapprox_printed), "Iapprox is not printed from the code"


    # Load all relevant files and restrict data to max 10th order
    Iexact_reference     = np.array(np.load(filename_Iexact))
    freqw = Iexact_reference[3]
    # All indices between 0 and 10th order
    freq_idx = np.where(np.logical_and(0 <= freqw, freqw <= 10))[0]

    Iexact_E_dir_reference = Iexact_reference[6][freq_idx]
    Iexact_ortho_reference = Iexact_reference[7][freq_idx]

    Iexact_printed       = np.array(np.load(filename_Iexact_printed))
    Iexact_E_dir_printed = Iexact_printed[6][freq_idx]
    Iexact_ortho_printed = Iexact_printed[7][freq_idx]

    Iapprox_reference       = np.array(np.load(filename_Iapprox))
    Iapprox_E_dir_reference = Iapprox_reference[6][freq_idx]
    Iapprox_ortho_reference = Iapprox_reference[7][freq_idx]

    Iapprox_printed       = np.array(np.load(filename_Iapprox_printed))
    Iapprox_E_dir_printed = Iapprox_printed[6][freq_idx]
    Iapprox_ortho_printed = Iapprox_printed[7][freq_idx]

    print("\n\nMaxima of the emission spectra: ", 
          "\nexact  E_dir: ", np.amax(np.abs(Iexact_E_dir_reference))  ,
          "\nexact  ortho: ", np.amax(np.abs(Iexact_ortho_reference))  ,
          "\napprox E_dir: ", np.amax(np.abs(Iapprox_E_dir_reference)) ,
          "\napprox ortho: ", np.amax(np.abs(Iapprox_ortho_reference)) )

    Iexact_relerror      = (np.abs(Iexact_E_dir_printed    + Iexact_ortho_printed   ) + 1.0E-90) / \
                           (np.abs(Iexact_E_dir_reference  + Iexact_ortho_reference ) + 1.0E-90) - 1
    Iapprox_relerror     = (np.abs(Iapprox_E_dir_printed   + Iapprox_ortho_printed  ) + 1.0E-90) / \
                           (np.abs(Iapprox_E_dir_reference + Iapprox_ortho_reference) + 1.0E-90) - 1

    Iexact_max_relerror  = np.amax(np.abs(Iexact_relerror))
    Iapprox_max_relerror = np.amax(np.abs(Iapprox_relerror))

    print("\n\nTesting the exact emission spectrum I(omega):", 
      "\n\nThe maximum relative deviation between the computed and the reference spectrum is:", Iexact_max_relerror,
        "\nThe threshold is:                                                                 ", threshold_rel_error, "\n")

    assert Iexact_max_relerror < threshold_rel_error, "The exact emission spectrum is not matching."

    print("Testing the approx. emission spectrum I(omega):", 
      "\n\nThe maximum relative deviation between the computed and the reference spectrum is:", Iapprox_max_relerror,
        "\nThe threshold is:                                                                 ", threshold_rel_error, "\n")

    assert Iapprox_max_relerror < threshold_rel_error, "The approx. emission spectrum is not matching."

    shutil.rmtree(testdir + '/__pycache__')
    for E0_dirname   in glob.glob(testdir + '/E0*'):   shutil.rmtree(E0_dirname)
    for PATH_dirname in glob.glob(testdir + '/PATH*'): shutil.rmtree(PATH_dirname)

    os.remove(testdir + '/' + glob.glob("Iexact_*")[0])
    os.remove(testdir + '/' + glob.glob("Iapprox_*")[0])
    for params_output in glob.glob(testdir + '/params_*'): os.remove(params_output)

    print('Test passed successfully.'
          '\n\n=====================================================\n\n')

    os.chdir("..")

    # reset mode of the script
    #if args.reset:
    #    os.system('sed -n -i \'1p\' ' + filename_reference)
    #    os.system('cat ' + filename + " >> " + filename_reference)

    # # normal test mode if the script
    # else:
    #   with open(filename) as f:
    #       count = 0
    #       for line in f:
    #           count += 1
    #           fields = line.split()
    #           value_test = float(fields[1])

    #           with open(filename_reference) as f_reference:

    #               count_reference = 0
    #               for line_reference in f_reference:
    #                   count_reference += 1
    #                   fields_reference = line_reference.split()

    #                   # we have the -1 because there is the header with executing command
    #                   # in the reference file
    #                   if count == count_reference-1:
    #                       value_reference = float(fields_reference[1])

    #                       abs_error = np.abs(value_test - value_reference)
    #                       rel_error = abs_error/np.abs(value_reference)

    #                       check_abs = abs_error < threshold_abs_error
    #                       check_rel = rel_error < threshold_rel_error

    #                       print('{:<15} {:>25} {:>25} {:>25} {:>25}'.format(fields_reference[0], \
    #                             value_reference, value_test, rel_error, abs_error))

    #                       assert check_abs or check_rel, \
    #                              "\n\nAbsolute and relative error of variable number "+str(count)+\
    #                              " compared to reference too big:"\
    #                              "\n\nRelative error: "+str(rel_error)+" and treshold: "+str(threshold_rel_error)+\
    #                              "\n\nAbsolute error: "+str(abs_error)+" and treshold: "+str(threshold_abs_error)

    #           f_reference.close()

    #   print("\n\nTest passed successfully.\n\n")

    #   f.close()

def main():

#    parser = argparse.ArgumentParser(description='Test script')
#    parser.add_argument('-reset', default=False, action='store_true',
#                        help=('Flag to reset all *.reference files in ./' + testdir +
#                              '. Needed: Put all .reference files you want to reset/update'
#                              'in ./' + testdir  + 'and insert the command to execute the'
#                              ' main script in the first line of'
#                              'the .reference file. The reset mode of this script'
#                              'will insert the lines of the test file after the first'
#                              'line (which contains the command to execute the main'
#                              'script).'))
#    args = parser.parse_args()


    dirpath = os.getcwd()

    print('\n\n=====================================================\n\n SBE CODE TESTER'
          '\n\n Executed in the directory:\n\n '+dirpath+
          '\n\n=====================================================\n\n')

    count = 0

    for subdir, dirs, files in os.walk(dirpath+'/tests'):
        for dir in sorted(dirs):
            testdir = os.path.join(subdir, dir)
            count += 1
            check_test(testdir)

    assert count > 0, 'There are no test files with ending .reference in directory ./' + testdir

if __name__ == "__main__":
    main()
