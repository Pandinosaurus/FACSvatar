"""Cleans an OpenFace .csv file

- Removes unnecessary columns
- Removes low confidence rows
- Normalizes AU interval to 0-1 from 0-5

Saves cleaned csv in path/to/folder_clean
"""

# Copyright (c) Stef van der Struijk.
# License: GNU Lesser General Public License


import os
from pathlib import Path
import pandas as pd


# clean csv output of OpenFace, remove irrelevant columns
class FilterCSV:
    def __init__(self, col_keep=None):  # , dir_processed, col_keep, dir_timestamp
        """Transform csv to Panda dataframe which can be accessed by other functions

        :param csv_file: Path object to csv file
        :param col_keep:

        If cleaned csv exist, skip cleaning and load directly as dataframe
        """
        # dir_processed: where to find .csv files
        # col_keep: columns to keep in .csv file [AU*_r, pose, gaze]

        if col_keep is None:
            col_keep = ['AU.*_r', 'pose_R.*', 'gaze_angle*']

        self.df_csv = None
        # Action Units and head rotation
        self.col_keep = col_keep  # , 'gaze_angle*'

        #   skip cleaning and load clean as dataframe
        # change string to path object
        # csv_file = Path(csv_file)

        # csv_clean = csv_file
        # # add _clean to parent directory
        # print(csv_clean.parts[-2])
        # # csv_clean.parts[-2] = Path(str(csv_clean.parts[-2]) + "_clean")
        # csv_clean.parts[-2] = csv_clean.parts[-2] + "_clean"

        # csv_clean = Path(str(csv_file.parents[0]) + '_clean/' + csv_file.parts[-1])

        # if csv_clean.exists():  # Path(csv_file[:-4] + "_clean.csv")
        #     print("OpenFace .csv already cleaned")
        #     #self.df_csv = pd.read_csv(csv_file[:-4] + "_clean.csv")
        #     self.df_csv = pd.read_csv(csv_clean)
        #
        # # load csv as dataframe and clean
        # else:
        #     print("Cleaning OpenFace .csv")
        #     self.clean_controller(csv_file, csv_clean)

    # removes space in header, e.g. ' confidence' --> 'confidence'
    def clean_header_space(self):
        self.df_csv.columns = self.df_csv.columns.str.strip()

    # remove rows where success == 0 and confidence < 0.8
    def clean_unsuccessful(self):
        self.df_csv.drop(self.df_csv[(self.df_csv.success == 0) | (self.df_csv.confidence < 0.8)].index,
                        inplace=True)

    # remove unnecessary columns
    def clean_columns(self):
        if len(self.col_keep) >= 1:
            # doesn't include AU28_c (lip suck), which has no AU28_r
            reg = "(frame)|(timestamp)|(confidence)|(success)|{}" \
                .format("|".join("({})".format(c) for c in self.col_keep))
        else:
            reg = "(frame)|(timestamp)|(confidence)"
        # print("regex col filter: {}".format(reg))
        self.df_csv = self.df_csv.filter(regex=reg)

    def match_index_frame(self):
        self.df_csv['frame'] = self.df_csv.index

    # get AU values and set interval from 0-5 to 0-1
    def reset_au_interval(self):
        c = self.df_csv.columns.str.contains("AU.*_r")
        self.df_csv.loc[:, c] /= 5

    # save cleaned dataframe as csv
    def csv_save(self, csv_clean):
        """

        :param csv_clean: Path object for saving cleaned csv
        """

        #   get dir without file name
        # windows
        # if os.name == 'nt':
        #     path_list = csv_file.split('\\')
        # # other OS
        # else:
        #     path_list = csv_file.split('/')
        #
        # dir_output = join(path_list)

        # create dir preprocessed if not existing, Python 3.2+
        os.makedirs(csv_clean.parents[0], exist_ok=True)

        # df.loc[:, df.columns.str.contains('a')]
        # self.df_csv.to_csv(csv_file[:-4] + "_clean.csv", index=False)  # , columns=[]
        self.df_csv.to_csv(csv_clean, index=False)

        # calls all cleaning + save functions
    def clean_controller(self, csv_raw, csv_folder_clean):
        """ Manages cleaning of raw openface csv file

        :param csv_raw: path to raw file
        :param csv_folder_clean: path to folder with cleaned files
        :return:
        """

        print("Cleaning: {} and save to {}".format(csv_raw, csv_folder_clean))
        self.df_csv = pd.read_csv(csv_raw)

        # removes space in header, e.g. ' confidence' --> 'confidence'
        self.clean_header_space()

        # remove rows with bad AU tracking TODO do something with failed tracking
        #self.clean_unsuccessful()

        # remove non-speech rows based on timestamps provided with dataset
        # self.clean_nonspeech(file)

        # dataframe with only c_keep columns
        self.clean_columns()

        # Set frame -1 to match index
        self.match_index_frame()

        # divide AU*_r by 5 (range from 0-1 instead of 0-5)
        self.reset_au_interval()

        # save cleaned dataframe; add csv file name to clean path
        self.csv_save(csv_folder_clean / csv_raw.name)
