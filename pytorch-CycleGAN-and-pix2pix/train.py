"""General-purpose training script for image-to-image translation.

This script works for various models (with option '--model': e.g., pix2pix, cyclegan, colorization) and
different datasets (with option '--dataset_mode': e.g., aligned, unaligned, single, colorization).
You need to specify the dataset ('--dataroot'), experiment name ('--name'), and model ('--model').

It first creates model, dataset, and visualizer given the option.
It then does standard network training. During the training, it also visualize/save the images, print/save the loss plot, and save models.
The script supports continue/resume training. Use '--continue_train' to resume your previous training.

Example:
    Train a CycleGAN model:
        python train.py --dataroot ./datasets/maps --name maps_cyclegan --model cycle_gan
    Train a pix2pix model:
        python train.py --dataroot ./datasets/facades --name facades_pix2pix --model pix2pix --direction BtoA

See options/base_options.py and options/train_options.py for more training options.
See training and test tips at: https://github.com/junyanz/pytorch-CycleGAN-and-pix2pix/blob/master/docs/tips.md
See frequently asked questions at: https://github.com/junyanz/pytorch-CycleGAN-and-pix2pix/blob/master/docs/qa.md
"""
import time
from options.train_options import TrainOptions
from data import create_dataset
from models import create_model
from util.visualizer import Visualizer

if __name__ == '__main__':
    opt = TrainOptions().parse()   # get training options
    dataset = create_dataset(opt)  # create a dataset given opt.dataset_mode and other options
    dataset_size = len(dataset)    # get the number of images in the dataset.
    print('The number of training images = %d' % dataset_size)

    model = create_model(opt)      # create a model given opt.model and other options
    model.setup(opt)               # regular setup: load and print networks; create schedulers
    visualizer = Visualizer(opt)   # create a visualizer that display/save images and plots
    total_iters = 0                # the total number of training iterations

    for epoch in range(opt.epoch_count, opt.n_epochs + opt.n_epochs_decay + 1):    # outer loop for different epochs; we save the model by <epoch_count>, <epoch_count>+<save_latest_freq>
        epoch_start_time = time.time()  # timer for entire epoch
        iter_data_time = time.time()    # timer for data loading per iteration
        epoch_iter = 0                  # the number of training iterations in current epoch, reset to 0 every epoch
        visualizer.reset()              # reset the visualizer: make sure it saves the results to HTML at least once every epoch

        for i, data in enumerate(dataset):  # inner loop within one epoch
            iter_start_time = time.time()  # timer for computation per iteration
            if total_iters % opt.print_freq == 0:
                t_data = iter_start_time - iter_data_time

            total_iters += opt.batch_size
            epoch_iter += opt.batch_size
            model.set_input(data)         # unpack data from dataset and apply preprocessing
            model.optimize_parameters()   # calculate loss functions, get gradients, update network weights

            if total_iters % opt.display_freq == 0:   # display images on visdom and save images to a HTML file
                save_result = total_iters % opt.update_html_freq == 0
                model.compute_visuals()
                visualizer.display_current_results(model.get_current_visuals(), epoch, save_result)

            if total_iters % opt.print_freq == 0:    # print training losses and save logging information to the disk
                losses = model.get_current_losses()
                t_comp = (time.time() - iter_start_time) / opt.batch_size
                visualizer.print_current_losses(epoch, epoch_iter, losses, t_comp, t_data)
                if opt.display_id > 0:
                    visualizer.plot_current_losses(epoch, float(epoch_iter) / dataset_size, losses)

            if total_iters % opt.save_latest_freq == 0:   # cache our latest model every <save_latest_freq> iterations
                print('saving the latest model (epoch %d, total_iters %d)' % (epoch, total_iters))
                save_suffix = 'iter_%d' % total_iters if opt.save_by_iter else 'latest'
                model.save_networks(save_suffix)

            iter_data_time = time.time()
        if epoch % opt.save_epoch_freq == 0:              # cache our model every <save_epoch_freq> epochs
            print('saving the model at the end of epoch %d, iters %d' % (epoch, total_iters))
            model.save_networks('latest')
            model.save_networks(epoch)

        print('End of epoch %d / %d \t Time Taken: %d sec' % (epoch, opt.n_epochs + opt.n_epochs_decay, time.time() - epoch_start_time))
        model.update_learning_rate()                     # update learning rates at the end of every epoch.


# new training function (implements the pseudocode on the paper)
if __name__ == '__main_Binkowski__':

    def inf_data(data_iter, data_loader):
        try:
            data=next(data_iter)
        except StopIteration:
            data_iter = iter(data_loader)
            data = next(data_iter)

        return data, data_iter

    opt = TrainOptions().parse()   # get training options
    dataset = create_dataset(opt)  # create a dataset given opt.dataset_mode and other options
    dataset_size = len(dataset)    # get the number of images in the dataset.
    print('The number of training images = %d' % dataset_size)

    model = create_model(opt)      # create a model given opt.model and other options
    model.setup(opt)               # regular setup: load and print networks; create schedulers
    visualizer = Visualizer(opt)   # create a visualizer that display/save images and plots
    gen_iters = 0                # the total number of generator iterations

    n = 20000
    d = 5
    learning_rate_update_freq = 1000
    opt.display_freq = 20
    opt.print_freq = 20
    opt.save_latest_freq = 1000
    opt.save_epoch_freq = 1000

    data_time = time.time() # timer for data loading 
    it_gen = iter(dataset) #iterator for outer cycle
    it_dis = iter(dataset) #iterator for inner cycle
    t_data = (time.time() - data_time)/(1+d)


    for k in range(n):    # outer loop for different generator steps; we save the model by <epoch_count>, <epoch_count>+<save_latest_freq>
        k_start_time = time.time()  # timer for entire generator step
        visualizer.reset()              # reset the visualizer: make sure it saves the results to HTML at least once every epoch
        disc_iters = 0                  # the number of discriminator iterations in current gen. iteration, reset to 0 every time

        #data = next(it_gen)
        data, it_gen = inf_data(it_gen, dataset)
        model.set_input(data)         # unpack data from dataset and apply preprocessing
        model.optimize_parameters_GW()   # calculate loss functions, get gradients, update network weights
        gen_iters += opt.batch_size

        for j in range(d):  # inner loop within one generator step
            j_start_time = time.time()  # timer for computation per discriminator step

            #data = next(it_dis)
            data, it_dis = inf_data(it_dis, dataset)
            model.set_input(data)         # unpack data from dataset and apply preprocessing
            model.optimize_parameters_D()   # calculate loss functions, get gradients, update network weights
            disc_iters += opt.batch_size

            if j==0:
                if gen_iters % opt.display_freq == 0:   # display images on visdom and save images to a HTML file
                    save_result = gen_iters % opt.update_html_freq == 0
                    model.compute_visuals()
                    visualizer.display_current_results(model.get_current_visuals(), k, save_result)

                if gen_iters % opt.print_freq == 0:    # print training losses and save logging information to the disk
                    losses = model.get_current_losses()
                    t_comp = (time.time() - j_start_time) / opt.batch_size
                    visualizer.print_current_losses(k, disc_iters, losses, t_comp, t_data)
                    if opt.display_id > 0:
                        visualizer.plot_current_losses(k, float(disc_iters) / dataset_size, losses)

                if gen_iters % opt.save_latest_freq == 0:   # cache our latest model every <save_latest_freq> iterations
                    print('saving the latest model (G iteration %d, total_iters %d)' % (k, gen_iters))
                    save_suffix = 'iter_%d' % gen_iters if opt.save_by_iter else 'latest'
                    model.save_networks(save_suffix)

            iter_data_time = time.time()
        if k % opt.save_epoch_freq == 0:              # cache our model every <save_epoch_freq> epochs
            print('saving the model at the end of G iteration %d, iters %d' % (k, gen_iters))
            model.save_networks('latest')
            model.save_networks(k)

        print('End of G iteration %d / %d \t Time Taken: %d sec' % (k, opt.n_epochs + opt.n_epochs_decay, time.time() - k_start_time))
        if gen_iters % learning_rate_update_freq == 0:
            model.update_learning_rate()                     # update learning rates at the end of every epoch.


