# -*- coding: utf-8 -*-

#
# * Copyright (c) 2009-2017. Authors: see NOTICE file.
# *
# * Licensed under the Apache License, Version 2.0 (the "License");
# * you may not use this file except in compliance with the License.
# * You may obtain a copy of the License at
# *
# *      http://www.apache.org/licenses/LICENSE-2.0
# *
# * Unless required by applicable law or agreed to in writing, software
# * distributed under the License is distributed on an "AS IS" BASIS,
# * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# * See the License for the specific language governing permissions and
# * limitations under the License.
# */


__author__          = "Vanhee Laurent <laurent.vanhee@student.uliege.ac.be>"
__copyright__       = "Copyright 2010-2017 University of Liège, Belgium, http://www.cytomine.be/"


import os
import config
import sys
import numpy as np
import image_data
from pygazeanalyser.gazeplotter import save_heatmap
import gc
import datetime

class User_data:
    """
    Class containing data on a user
    """
    def __init__(self, image_data_list, user_id, manager, y_vars, m_vars, x_vars):
        """
        Constructor, inits the object
        :param image_data_list: list containing image_dat objects
        :param user_id: user cytomine id
        :param manager: data_manager object
        :param practical: exam results
        :param theory: exam results
        :param f_name: first name
        :param l_name: last name
        :param email: email address
        """
        self.positions = {}
        self.user_annotations = {}
        self.user_descriptions = {}
        self.time_on_img = {}
        self.user_id = user_id
        self.manager = manager
        self.image_data = {}
        self.y_vars = y_vars
        self.m_vars = m_vars
        self.x_vars = x_vars

        # fill positions dict
        for image in image_data_list:
            if image.user_positions.get(str(user_id)) is not None:
                pos = image.user_positions[str(user_id)]
                im_id = image.image_id
                self.positions[str(im_id)] = pos
            if image.user_annotations.get(str(user_id)) is not None:
                annot = image.user_annotations[str(user_id)]
                im_id = image.image_id
                self.user_annotations[str(im_id)] = annot
            if image.user_descriptions.get(str(user_id)) is not None:
                desc = image.user_descriptions[str(user_id)]
                im_id = image.image_id
                self.user_descriptions[str(im_id)] = desc


    def nb_ims_visited(self):
        """
        finds the number of positions that have positions in them
        :return: the number of images with positions
        """
        return len(self.positions)


    def total_nb_positions(self):
        """
        Gets the total number of positions over all the images
        :return: Nb pos
        """
        ret = 0
        for im in self.positions.values():
            ret += len(im['x'])
        return ret


    def median_nb_positions(self):
        """
        Calculates the median number of positions over all the images visitied
        :return: median
        """
        if self.nb_ims_visited() == 0:
            return 0

        # put positions in an array
        positions = np.zeros(self.nb_ims_visited())
        i = 0
        for im in self.positions.values():
            positions[i] = len(im['x'])
            i += 1
        # sort positions
        positions = np.sort(positions)

        # return position number in the middle (median)
        return positions[np.int(self.nb_ims_visited()/2)]


    def avg_nb_positions_visited(self):
        """
        Calculates the average number of positions over all the images visited
        :return: avg
        """
        if self.nb_ims_visited() == 0:
            return 0
        return float(self.total_nb_positions()) / float(self.nb_ims_visited())


    def avg_nb_positions(self):
        """
        Calculates the average number of positions out of all the images
        :return: avg2
        """
        return float(self.total_nb_positions()) / float(self.manager.nb_images())


    def total_nb_user_annotations(self):
        """
        Gets the total number of user_annotations over all the images
        :return: Nb pos
        """
        ret = 0
        for im in self.user_annotations.values():
            ret += len(im['x'])
        return ret


    def median_nb_user_annotations(self):
        """
        Calculates the median number of user_annotations over all the images visited
        :return: median
        """
        # put user_annotations in an array
        user_annotations = np.zeros(self.manager.nb_images)
        i = 0
        for im in self.user_annotations.values():
            user_annotations[i] = len(im['x'])
            i += 1
        # sort user_annotations
        user_annotations = np.sort(user_annotations)

        # return user_annotation number in the middle (median)
        return user_annotations[np.int(self.manager.nb_images/2)]


    def avg_nb_user_annotations(self):
        """
        Calculates the average number of user_annotations out of all the images
        :return: avg2
        """
        return float(self.total_nb_user_annotations()) / float(self.manager.nb_images)


    def total_nb_user_descriptions(self):
        """
        Gets the total number of user_descriptions over all the images
        :return: Nb pos
        """
        ret = 0
        for im in self.user_descriptions.values():
            ret += len(im['description'])
        return ret


    def median_nb_user_descriptions(self):
        """
        Calculates the median number of user_descriptions over all the images visited
        :return: median
        """
        # put user_description in an array
        user_descriptions = np.zeros(self.manager.nb_images)
        i = 0
        for im in self.user_annotations.values():
            user_descriptions[i] = len(im['description'])
            i += 1
        # sort user_descriptions
        user_descriptions = np.sort(user_descriptions)

        # return user_description number in the middle (median)
        return user_descriptions[np.int(self.manager.nb_images/2)]


    def avg_nb_user_descriptions(self):
        """
        Calculates the average number of user_descriptions out of all the images
        :return: avg2
        """
        return float(self.total_nb_user_descriptions()) / float(self.manager.nb_images)


    def aggr_user_description(self):
        """
        Gets informations (avg, median, total) of words and chars of user_description made by an user
        :param im_id: image id
        :return: 1) total words
                 2) average words
                 3) median words
                 4) total chars
                 5) average chars
                 6) median chars
                 7) total nb of medias
        """
        total_description_word = None
        total_description_char = None
        avg_words_description = None
        avg_chars_description = None
        median_words_description = None
        median_chars_description = None
        total_description_media = 0

        descriptions = []
        for img in self.user_descriptions:
            descriptions.extend(self.user_descriptions[img]['description'])
            total_description_media = total_description_media + sum(self.user_descriptions[img]['media'])
 
        #total nb of word
        total_description_word = sum(list(map(lambda x: len(x.split()), descriptions)))
        #total nb of char
        total_description_char = sum(list(map(lambda x: len(x.strip().decode("utf-8")), descriptions)))
        if self.total_nb_user_descriptions() == 0:
            return total_description_word, 0, 0, total_description_char, 0, 0, 0

        #avg ng of word
        avg_words_description = float(total_description_word)/float(self.total_nb_user_descriptions())
        #avg nb of char
        avg_chars_description = float(total_description_char)/float(self.total_nb_user_descriptions())
        #median nb of words & chars
        # put them in an array
        chars = np.zeros(self.total_nb_user_descriptions())
        words = np.zeros(self.total_nb_user_descriptions())
        i = 0
        for desc in descriptions:
            chars[i] = len(desc.strip().decode("utf-8"))
            words[i] = len(desc.split())
            i += 1
        # sort them
        chars = np.sort(chars)
        words = np.sort(words)

        # return position number in the middle (median)
        median_words_description = words[np.int(self.total_nb_user_descriptions()/2)]
        median_chars_description = chars[np.int(self.total_nb_user_descriptions()/2)]

        return total_description_word, avg_words_description, median_words_description, total_description_char, avg_chars_description, median_chars_description,total_description_media


    def time_spent(self, im_id):
        """
        Calculates total time spent on an image
        :param im_id: image id
        :return: time in seconds
        """
        if im_id not in self.positions:
            return 0.0

        positions = self.positions[im_id]
        timestamps = positions['timestamp']
        i = 1
        time_on_image = 0.0
        while i < len(timestamps):
            ## timestamps are spaced at a interval of a maximum 5000ms
            if timestamps[i] - timestamps[i - 1] < 6000:
                time_on_image += timestamps[i] - timestamps[i - 1]
                i += 1
            else:
                i += 2
        self.time_on_img[im_id] = time_on_image/1000.0
        return time_on_image/1000.0


    def total_time_spent(self):
        """
        Calculates total time spent on images
        :return: total time
        """
        ret = 0.0
        for im_id in self.positions:
            if im_id in self.time_on_img:
                ret += self.time_on_img[im_id]
            else:
                ret += self.time_spent(im_id)
        return ret


    def avg_time_spent(self):
        """
        Calculates the average time spent on images relative to all images visited
        :return: avg
        """
        if self.nb_ims_visited() == 0:
            return 0
        return float(self.total_time_spent()) / float(self.nb_ims_visited())


    def median_time_spent(self):
        """
        Calculates median time spent on images relative to all images visited
        :return: median
        """
        if self.nb_ims_visited() == 0:
            return 0

        time_array = np.zeros(self.nb_ims_visited())
        i = 0
        for im_id in self.positions:
            if im_id in self.time_on_img:
                time_array[i] = self.time_on_img[im_id]
            else:
                time_array[i] = self.time_spent(im_id)
            i += 1
        time_array = np.sort(time_array)

        return time_array[np.int(self.nb_ims_visited()/2)]


    def zoom_position_number(self):
        """
        For each zoom level, calculates the total number of positions
        :return: positions nb for each zoom in an array
        """
        ret = np.zeros(config.MAX_ZOOM)
        for im_id in self.positions:
            p = self.positions[im_id]
            zooms = p['zoom']
            for i in range(len(zooms)):
                ret[zooms[i] - 1] += 1
        return ret


    def zoom_position_number_avg(self):
        """
        For each zoom level, calculates the average number of positions
        :return: position averages for each zoom in an array
        """
        if self.nb_ims_visited() == 0:
            return np.zeros(config.MAX_ZOOM)
        return self.zoom_position_number()/np.float(self.nb_ims_visited())


    def zoom_position_number_median(self):
        """
        For each zoom level, calculates the median number of positions
        :return: position medians for each zoom in an array
        """
        ret = np.zeros(config.MAX_ZOOM)
        if self.nb_ims_visited() == 0:
            return ret
        zooms = []
        for i in range(config.MAX_ZOOM):
            zooms.append([])
        # fills lists with positions
        for im_id in self.positions:
            p = self.positions[im_id]
            z = p['zoom']
            vals = np.zeros(config.MAX_ZOOM)
            for i in range(len(z)):
                vals[np.int(z[i] - 1)] += 1
            for i in range(config.MAX_ZOOM):
                zooms[i].append(vals[i])
        # sort each list and select middle
        for i in range(config.MAX_ZOOM):
            list_im = zooms[i]
            list_im.sort()
            ret[i] = list_im[int(len(list_im)/2)]
        return ret


    def zoom_position_avg(self):
        """
        Average zoom level relative to all images visited
        :return: zoom avg
        """
        ret = 0
        total = 0
        for im_id in self.positions:
            p = self.positions[im_id]
            zooms = p['zoom']
            for i in range(len(zooms)):
                ret += zooms[i]
                total += 1
        if total == 0:
            return 0
        return float(ret)/float(total)


    def zoom_position_median(self):
        """
        Calculates the median zoom relative to  all images visited
        :return: zoom median
        """
        ret = []
        total = 0
        for im_id in self.positions:
            p = self.positions[im_id]
            zooms = p['zoom']
            for i in range(len(zooms)):
                ret.append(zooms[i])
                total += 1

        ret.sort()
        if total == 0:
            return 0
        return ret[int(total/2)]


    def save_all_heatmaps_by_user(self):
        """
        Saves all heatmaps in image files, this method compares all heatmaps associated to this user
        and outputs images based on the minimums and maximums from all heatmaps. It also applies a logarithmic
        normalizer because of some very high values compared to others which affects scaling
        :return: None
        """
        # prepare dirs
        dir = config.WORKING_DIRECTORY  + self.manager.project_name + "/users/"
        if not os.path.exists(dir):
            os.makedirs(dir)
        dir = dir + "user_" + self.user_id + "/"
        if not os.path.exists(dir):
            os.makedirs(dir)
        dir = dir + "gazemaps_image_method/"
        if not os.path.exists(dir):
            os.makedirs(dir)

        max_val = 0
        avg_val = 0
        l = 0
        # determines an average value for all the ln heatmaps
        # determines the highest value found on all the heatmaps
        for im_id in self.image_data:
            pos = self.image_data[im_id].user_positions[self.user_id]
            heatmap = np.copy(pos['heatmap'])
            heatmap = heatmap + 1
            heatmap = np.log(heatmap)
            tmp = np.max(heatmap)
            max_val = max(tmp, max_val)
            if len(heatmap[heatmap > 0]) > 0:
                avg_val = np.mean(heatmap[heatmap > 0])
                l = l + 1
            del heatmap
        if l == 0:
            gc.collect()
            return

        avg_val = avg_val/l
        # Save all heatmaps while taking to account max and avg
        for im_id in self.image_data:
            rgb_im = self.image_data[im_id].image.convert('RGB')
            rgb_im.save('converted_image.jpg')

            out = dir + im_id + "_heatmap.png"
            pos = self.image_data[im_id].user_positions[self.user_id]
            heatmap = np.copy(pos['heatmap'])
            heatmap = heatmap + 1
            heatmap = np.log(heatmap)
            heatmap[0][0] = max_val
            save_heatmap(heatmap, (self.image_data[im_id].rescaled_width, self.image_data[im_id].rescaled_height), imagefile='converted_image.jpg', savefilename=out, alpha=0.5, avg=avg_val, annotations=self.image_data[im_id].ref_annotations)
            del heatmap
            os.remove('converted_image.jpg')
        gc.collect()


    def total_annotation_actions(self):
        """
        Calculates the total number of annotation actions done by the user
        :return: Nb ann
        """
        ret = 0
        for im_id in self.image_data:
            im = self.image_data[im_id]

            if self.user_id in im.user_actions:
                actions = im.user_actions[self.user_id]
                ret += len(actions['id'])

        return ret


    def avg_annotation_actions(self):
        """
        Calculates the average number of annotation actions relative to all images visited
        :return: avg ann
        """
        if self.nb_ims_visited() == 0:
            return 0
        return float(self.total_annotation_actions())/float(self.nb_ims_visited())


    def median_annotation_actions(self):
        """
        Calculates the median number of annotation actions relative to all images visited
        :return: median ann
        """
        if self.nb_ims_visited() == 0:
            return 0
        ret = np.zeros(self.nb_ims_visited())
        i = 0
        for im_id in self.image_data:
            im = self.image_data[im_id]
            if self.user_id in im.user_actions:
                actions = im.user_actions[self.user_id]
                ret[i] = len(actions['id'])
            i += 1
        ret = np.sort(ret)
        return ret[np.int(len(ret)/2)]


    def number_of_positions(self, im_id):
        """
        Gets number of positions for a user in an image
        :param im_id: image id
        :return: number of positions
        """
        if im_id in self.positions:
            positions = self.positions[im_id]
            return len(positions['x'])
        else:
            return 0


    def number_of_annotation_actions(self, im_id):
        """
        Gets number of annotations for a user in an image
        :param im_id: image id
        :return: number of annotations
        """
        if im_id not in self.image_data:
            return 0

        im = self.image_data[im_id]
        if self.user_id not in im.user_actions:
            return 0

        ann = im.user_actions[self.user_id]
        return len(ann['id'])


    def number_of_positions_at_zoom(self, im_id, zoom):
        """
        Gets number of positions for a user in an image at a particular zoom
        :param im_id: image id
        :return: number of positions
        """
        if im_id in self.positions:
            positions = self.positions[im_id]['zoom']
            nb = 0
            for i in range(len(positions)):
                if int(positions[i]) == zoom:
                    nb += 1
            return nb
        else:
            return 0

    def relative_time_worked(self):
        """
        Calculates the relative time worked features for night, late and morning for this user
        :return: night, late, morning
        """
        tot = 0
        nb_night = 0
        nb_late = 0
        nb_morning = 0

        for pos_id in self.positions:
            pos = self.positions[pos_id]
            tot += len(pos['timestamp'])
            for i in range(len(pos['timestamp'])):
                timestamp = pos['timestamp'][i]
                dt = datetime.datetime.fromtimestamp(float(timestamp / 1000.0))
                hour = dt.timetuple().tm_hour
                if hour >= 18 or hour < 6: # night
                    nb_night += 1
                if hour >= 1 and hour < 6: #late
                    nb_late += 1
                if hour >= 6 and hour < 12: #morning
                    nb_morning += 1

        if tot == 0:
            return 0, 0, 0

        nb_night = float(nb_night)/tot
        nb_late = float(nb_late)/tot
        nb_morning = float(nb_morning)/tot

        return nb_night, nb_late, nb_morning

    def nb_of_different_days_worked(self):
        """
        calculates and returns the total number of days on cytomine for this user
        :return: nb days
        """
        days = {}

        for pos_id in self.positions:
            pos = self.positions[pos_id]
            for i in range(len(pos['timestamp'])):
                timestamp = pos['timestamp'][i]
                dt = datetime.datetime.fromtimestamp(float(timestamp / 1000.0))
                day = dt.timetuple().tm_yday
                if day not in days:
                    days[day] = day

        return len(days)


    def number_user_annotations(self, im_id):
        """
        Gets number of user_annotations for a user in an image
        :param im_id: image id
        :return: Nb pos
        """
        if im_id in self.user_annotations:
            user_annotations = self.user_annotations[im_id]
            return len(user_annotations['x'])
        else:
            return 0

    def number_user_description(self, im_id):
        """
        Gets number of user_description for a user in an image
        :param im_id: image id
        :return: Nb pos
        """
        if im_id in self.user_descriptions:
            user_descriptions = self.user_descriptions[im_id]
            return len(user_descriptions['description'])
        else:
            return 0

    def aggr_user_description_of_image(self, im_id):
        """
        Gets informations (avg, median, total) of words and chars of user_description for a user in an image
        :param im_id: image id
        :return: 1) total words
                 2) average words
                 3) median words
                 4) total chars
                 5) average chars
                 6) median chars
        """
        total_description_word = None
        total_description_char = None
        avg_words_description = None
        avg_chars_description = None
        median_words_description = None
        median_chars_description = None
        if im_id in self.user_descriptions:
            descriptions = self.user_descriptions[im_id]['description']

            #total nb of word
            total_description_word = sum(list(map(lambda x: len(x.split()), descriptions)))
            #total nb of char
            total_description_char = sum(list(map(lambda x: len(x.strip().decode("utf-8")), descriptions)))
            if self.number_user_description(im_id) == 0:
                return total_description_word, 0, 0, total_description_char, 0, 0

            #avg ng of word
            avg_words_description = float(total_description_word)/float(self.number_user_description(im_id))
            #avg nb of char
            avg_chars_description = float(total_description_char)/float(self.number_user_description(im_id))
            #median nb of words & chars
            # put them in an array
            chars = np.zeros(self.number_user_description(im_id))
            words = np.zeros(self.number_user_description(im_id))
            i = 0
            for desc in descriptions:
                chars[i] = len(desc.strip().decode("utf-8"))
                words[i] = len(desc.split())
                i += 1
            # sort them
            chars = np.sort(chars)
            words = np.sort(words)

            # return position number in the middle (median)
            median_words_description = words[np.int(self.number_user_description(im_id)/2)]
            median_chars_description = chars[np.int(self.number_user_description(im_id)/2)]

        return total_description_word, avg_words_description, median_words_description, total_description_char, avg_chars_description, median_chars_description


    def __repr__(self):
        return "user :" + str(self.user_id) + ", positions :" + str(len(self.positions)) + ", links :" + str(len(self.image_data)) + "\n"

    def __str__(self):
        return "user :" + str(self.user_id) + ", positions :" + str(len(self.positions)) + ", links :" + str(len(self.image_data)) + "\n"
