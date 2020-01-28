# core stuff
import pandas as pd
import numpy  as np

# plotty stuff
import matplotlib.pyplot     as plt
import matplotlib.lines      as mlines
import matplotlib.transforms as mtransforms

# CONSTANTS
DATA_PATH = "./data/"

MODE_DESCRIPTION = {
    'bin' : "Binomial CQIs",
    'uni' : "Uniform CQIs"
}

LAMBDA_DESCRIPTION = {
    'l09' : "Lambda = 0.9",
    'l13' : "Lambda = 1.3",
    'l2'  : "Lambda = 2.0",
    'l5'  : "Lambda = 5.0"
}

MODE_PATH = {
    'bin' : "binomial/",
    'uni' : "uniform/"
}

LAMBDA_PATH = {
    'l09' : "lambda09/",
    'l13' : "lambda13/",
    'l2'  : "lambda2/",
    'l5'  : "lambda5/"
}

CSV_PATH = {
    'sca' : "sca/results.csv",
    'vec' : "vec/results.csv"
}

# Parse CSV file
def scalar_parse(cqi, pkt_lambda):
    path_csv = DATA_PATH + MODE_PATH[cqi] + LAMBDA_PATH[pkt_lambda] + CSV_PATH['sca']
    data = pd.read_csv(path_csv, usecols=['run', 'type', 'name', 'value'])
    
    # remove useless rows (first 100-ish rows)
    data = data[data.type == 'scalar']
    data.reset_index(inplace=True, drop=True)

    # clean name value
    data.name = data.name.apply(lambda x: x.split(':')[0])
    return data[['run', 'name', 'value']]


def describe_attribute(data, name):
    # print brief summary of attribute name (with percentiles and stuff)
    print(data[data.name == name].describe(percentiles=[.25, .50, .75, .95]))
    return


def lorenz(arr):
    # this divides the prefix sum by the total sum
    # this ensures all the values are between 0 and 1.0
    scaled_prefix_sum = arr.cumsum() / arr.sum()
    # this prepends the 0 value (because 0% of all people have 0% of all wealth)
    return np.insert(scaled_prefix_sum, 0, 0)




def lorenz_curve(data, attribute):
    # sort the data
    sorted_samples = data[data.name == attribute].sort_values(['value']).value

    # compute required stuff
    n = len(sorted_samples)
    T = sorted_samples.sum()
    x = [i/n for i in range(1, n+1)]
    y = sorted_samples.cumsum()/T

    # # plot lorenz curve
    # _, ax = plt.subplots() # ignore fig return value
    # ax.plot(x, y)
    
    # # add the 45deg line
    # line = mlines.Line2D([0, 1], [0, 1], color='red')
    # transform = ax.transAxes
    # line.set_transform(transform)
    # ax.add_line(line)
    
    plt.plot(x, y) # actual lorenz curve
    plt.plot([0, 0], [1, 1], 'k') # 45deg line

    # prettify the plot
    plt.title("Lorenz Curve for " + attribute)
    plt.show()
    return


def plot_ecdf(data, attribute):
    sorted_samples = list(data[data.name == attribute].sort_values(['value']).value)
    F_x = []
    n = len(sorted_samples)

    for x in sorted_samples:
        s = 0
        for i in range(0, n):
            s = s + 1 if sorted_samples[i] < x else s
        F_x.append(s/n)
    
    plt.plot(sorted_samples, F_x)
    return


def check_iid(data, attribute):
    samples = data[data.name == attribute].value
    pd.plotting.lag_plot(samples)
    plt.title("Lag-Plot for " + attribute)
    plt.show()

    pd.plotting.autocorrelation_plot(samples)
    plt.title("Autocorrelation plot for " + attribute)
    plt.show()
    return
    


def scalar_analysis(cqi_mode, pkt_lambda, verbose=0):
    # parse csv
    print("* * * Scalar analysis: ")
    print("+ - - - - - - - - - - - - - - - - - - - - - - - - - -")
    print("|  * CQI Generation : " + MODE_DESCRIPTION[cqi_mode])
    print("|  * Exponential packet interarrival : " + LAMBDA_DESCRIPTION[pkt_lambda])
    print("+ - - - - - - - - - - - - - - - - - - - - - - - - - -\n\n")

    clean_data = scalar_parse(cqi_mode, pkt_lambda)
    
    if(verbose > 1):
        print("Clean dataset for lambda2-scalar")
        print(clean_data.head())

    if(verbose > 0):
        print("** Info about mean throughput: ")
        describe_attribute(clean_data, 'throughput')

        print("** Info about mean response time: ")
        describe_attribute(clean_data, 'responseTime')
        
        print("** Info about mean num served user (throughput 2): ")
        describe_attribute(clean_data, 'NumServedUser')

    # check iid
    check_iid(clean_data, 'responseTime')
    check_iid(clean_data, 'throughput')
    check_iid(clean_data, 'NumServedUser')

    # plot lorenz curve for response time
    lorenz_curve(clean_data, 'responseTime')

    # end of analysis
    return


def all_ecdf(ds_list, attribute, labels=None):
    for ds in ds_list:
        plot_ecdf(ds, attribute)

    plt.title("ECDF for " + attribute)    
    if labels:
        plt.legend(labels)
    plt.show()
    return


def load_all_bin():
    return [scalar_parse('bin', 'l13'),
            scalar_parse('bin', 'l2'),
            scalar_parse('bin', 'l5')]


def load_all_uni():
    return [scalar_parse('uni', 'l09'),
            scalar_parse('uni', 'l2'),
            scalar_parse('uni', 'l5')]


def main():
    print("\n\nPerformance Evaluation - Python Data Analysis\n")
    
    scalar_analysis('bin', 'l5', verbose=1)

    # load all datasets of type UNIFORM
    datasets = load_all_uni()

    # print all ecdf all together  
    all_ecdf(datasets, 
             attribute='responseTime',
             labels=['L = 0.9', 'L = 2.0', 'L = 5.0'])

    # end
    return

if __name__ == '__main__':
    main()