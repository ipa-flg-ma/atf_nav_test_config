#!/usr/bin/python

"""
Created on Dec 15, 2017

@author: flg-ma
@attention: compare the output results of the ATF tests
@contact: albus.marcel@gmail.com (Marcel Albus)
@version: 1.2.0


#############################################################################################

History:
- v1.2.0: added filepath if/else in __init__
- v1.1.1: added bar annotations displaying the height
- v1.1.0: errorbar plot now normal bar plot with min and max values as bars
- v1.0.0: first push
"""

import os
import yaml
import pandas as pd
import matplotlib.pyplot as plt


class CompareConfig:
    def __init__(self, filepath=None):
        print '\033[94m' + '=' * 100 + '\033[0m'
        print '\033[94m' + '=' * 42 + ' Compare Config ' + '=' * 42 + '\033[0m'
        print '\033[94m' + '=' * 100 + '\033[0m'
        try:
            if filepath is None:
                self.pth = raw_input('Please enter Path to generated testcase output (e.g: \'/home/flg-ma/Test/\'): ')
            else:
                self.pth = filepath
            print 'Collecting directories in given path...'
            self.directories = os.walk(self.pth).next()[1]
        except StopIteration:  # catch error when there is no valid directory given
            exit('The directory path does not exist')

        print '=' * 100
        self.yaml_name = 'move_base_eband_params.yaml'
        self.do_params = ['max_vel_lin',
                          'max_vel_th',
                          'max_translational_acceleration',
                          'max_rotational_acceleration',
                          'scaled_radius_factor',
                          'eband_min_relative_bubble_overlap',
                          'kinematics_string']

    def collect_dataframe(self):
        '''
        collect a pandas dataframe from all the 'move_base_eband_parameter.yaml' files in a given directory
        :return: --
        '''
        df = pd.DataFrame({})  # create empty dataframe
        counter = 0
        for folder in self.directories:  # walk through all directories
            with open(self.pth + folder + '/' + self.yaml_name, 'r') as f:
                yaml_dict = yaml.load(f)  # save all the yaml data in a dictionary
            df = df.append(yaml_dict, ignore_index=True)  # save the dict in the df
            # increase counter
            counter += 1
            if counter % 20 == 0:  # output every 20 directories
                print 'Directories saved: ' + str(counter) + ' / ' + str(self.directories.__len__())
        # df.to_csv(self.pth + 'Config.csv')
        self.df = df.copy()  # save dataframe

    def plot_error_bar(self):
        '''
        plot an errorbar chart to show all the changed params from the config in a given directory
        :return: --
        '''
        df = self.df.copy()  # copy df

        columns = df.columns.tolist()
        for params in self.do_params:
            columns.remove(params)  # delete all unnecessary entries from the columns list
        df = df.drop(columns, axis=1)  # drop every column not changed

        df = df.drop('kinematics_string', axis=1) # because strings can't be displayed

        for col in df:
            df.loc[0, col] = df.max()[col]  # save max of column in first row
            df.loc[1, col] = df.min()[col]  # save min of column in second row
        df2 = df.loc[0:1, :].copy()  # copy only first 2 rows
        df2 = df2.transpose()  # transpose array

        print '=' * 100
        print df2.head(5)
        print '=' * 100
        df2 = df2.rename(columns={0:'max', 1:'min'})

        means = df.mean()  # means of all values
        print '\033[94m' + 'average values' + '\033[0m'
        print means
        print '=' * 100
        # print '\033[94m' + 'standard deviation' + '\033[0m'
        # print df.std()

        scale_factor = 1.0
        fig = plt.figure(222, figsize=(7.0 * scale_factor, 16.0 * scale_factor))
        ax1 = fig.add_subplot(111)
        ax = df2.plot.bar()
        for p in ax.patches:
            ax.annotate(str(p.get_height()), (p.get_x() * 1.005, p.get_height() * 1.015))
        plt.legend()
        plt.grid(True)
        plt.savefig(self.pth + 'ChangedValues.pdf', bbox_inches='tight')
        # plt.show()
        fig.clf()
        print '\033[92m' + '=' * 34 + ' Created Changed Value Barplot ' + '=' * 35 + '\033[0m'

    def main(self):
        self.collect_dataframe()
        self.plot_error_bar()


if __name__ == '__main__':
    st = CompareConfig()
    st.main()
