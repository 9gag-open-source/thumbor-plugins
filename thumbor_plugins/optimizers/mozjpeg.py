#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license


import os
import subprocess
import re

from thumbor.optimizers import BaseOptimizer
from thumbor.utils import logger
from PIL import Image


class Optimizer(BaseOptimizer):
    def __init__(self, context):
        super(Optimizer, self).__init__(context)

        self.runnable = True
        self.mozjpeg_path = self.context.config.MOZJPEG_PATH
        self.mozjpeg_level = self.context.config.MOZJPEG_QUALITY or '75'

        if not (os.path.isfile(self.mozjpeg_path) and os.access(self.mozjpeg_path, os.X_OK)):
            logger.error("ERROR mozjpeg path '{0}' is not accessible".format(self.mozjpeg_path))
            self.runnable = False

    def should_run(self, image_extension, buffer):
        return ('mozjpeg' in self.context.request.filters) and self.runnable

    def optimize(self, buffer, input_file, output_file):
        
        args_whitelist = ['sample', 'quant-table']
        mozjpeg = [filter for filter in self.context.request.filters.split(':') if filter.startswith('mozjpeg')]
        args = []

        if len(mozjpeg) > 0:
            mozjpeg = re.search(r'\((.*?)\)', mozjpeg[0]).group(1)

            for option in mozjpeg.split(','):
                option = option.split('=')

                if len(option) == 2 and option[0] in args_whitelist:
                    args.append('-' + option[0] + ' ' + option[1]) 
                else:
                    option[0] == 'quality'
                    self.mozjpeg_level = option[1]


        intermediary = output_file + '-intermediate'
        Image.open(input_file).save(intermediary, 'tga')
        command = '%s -quality %s %s -optimize %s > %s' % (
            self.mozjpeg_path,
            self.mozjpeg_level,
            ' '.join(args),
            intermediary,
            output_file,
        )
        with open(os.devnull) as null:
            #
            logger.debug("[MOZJPEG] running: " + command)
            subprocess.call(command, shell=True, stdin=null)
