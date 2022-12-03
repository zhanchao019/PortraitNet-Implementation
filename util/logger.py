'''
Code referenced from:
https://gist.github.com/gyglim/1f8dfb1b5c82627ae3efcfbbadb9f514
'''

import tensorflow as tf
import numpy as np
import scipy.misc
import pdb
try:
    from StringIO import StringIO # Python 2.7
except ImportError:
    from io import BytesIO # Python 3.x
from PIL import Image

class Logger(object):
    def __init__(self, log_dir):
        """Create a summary writer logging to log_dir."""
        self.writer = tf.summary.create_file_writer(log_dir)

    def scalar_summary(self, tag, value, step):
        """Log a scalar variable."""
        #pdb.set_trace()
        with self.writer.as_default():
            tf.summary.scalar(tag, value.to('cpu'), step=step)
            self.writer.flush()

    def image_summary(self, tag, images, step):
        """Log a list of images."""
        
        img_summaries = []
        #pdb.set_trace()
        for i, img in enumerate(images):
            # Write the image to a string
            try:
                s = StringIO()
            except:
                s = BytesIO()
            
            #scipy.misc.toimage(img).save(s, format="png") replace by 
        #pdb.set_trace()  

        #log
        tf.summary.image(name='%s/%d' % (tag, i),data=images)


    def histo_summary(self, tag, values, step, bins=1000):
        """Log a histogram of the tensor of values."""

        # Create a histogram using numpy
        counts, bin_edges = np.histogram(values, bins=bins)

        # Fill the fields of the histogram proto
        hist = tf.HistogramProto()
        hist.min = float(np.min(values))
        hist.max = float(np.max(values))
        hist.num = int(np.prod(values.shape))
        hist.sum = float(np.sum(values))
        hist.sum_squares = float(np.sum(values ** 2))

        # Drop the start of the first bin
        bin_edges = bin_edges[1:]

        # Add bin edges and counts
        for edge in bin_edges:
            hist.bucket_limit.append(edge)
        for c in counts:
            hist.bucket.append(c)

        # Create and write Summary
        summary = tf.Summary(value=[tf.Summary.Value(tag=tag, histo=hist)])
        self.writer.add_summary(summary, step)
        self.writer.flush()
        
if __name__ == '__main__':
    
    import model_rmppe as modellib
    import numpy as np
    
    logger = Logger('./logs')
    img = np.zeros((10, 3, 100, 100), dtype = np.uint8)
    
    print ('===========> loading model <===========')
    netmodel = modellib.get_model()
    for tag, value in netmodel.named_parameters():
        print (tag, value.data.cpu().numpy().shape)
    
    print ('===========> logger <===========')
    step = 0
    # (1) Log the scalar values
    info = {
        'loss': 0.5,
        'accuracy': 0.9
    }

    for tag, value in info.items():
        logger.scalar_summary(tag, value, step)

    # (2) Log values and gradients of the parameters (histogram)
    for tag, value in netmodel.named_parameters():
        tag = tag.replace('.', '/')
        logger.histo_summary(tag, value.data.cpu().numpy(), step)
        #logger.histo_summary(tag+'/grad', value.grad.cpu().numpy(), step)

    # (3) Log the images
    info = {
        'images': img
    }

    for tag, images in info.items():
        logger.image_summary(tag, images, step)