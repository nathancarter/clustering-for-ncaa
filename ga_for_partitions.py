
# there is randomness in GA
import random, statistics

# we want to time execution
import time, datetime

# we want execution to be faster
import pathos # this works only if you've done conda install pathos -c conda-forge

# how to choose a single element from a pair
def pick_one_from_pair ( pair ):
    return pair[random.randint( 0, 1 )]
# define breeding: uniform crossover
def uniform_crossover ( list1, list2 ):
    return [ pick_one_from_pair( genes ) for genes in zip( list1, list2 ) ]
# define mutation: with the given chance, tweak one gene in the individual
def mutate ( individual, chance, maximum ):
    if random.random() < chance:
        if random.random() < 0.5:
            i = random.randint( 0, len( individual ) - 1 )
            j = random.randint( 0, len( individual ) - 1 )
            individual[i], individual[j] = individual[j], individual[i]
        else:
            individual[random.randint( 0, len( individual ) - 1 )] = \
                random.randint( 0, maximum )
# how to pick the best fit from a population,
# assuming each element in the population is a (individual,fitness) pair
def get_score ( scored_individual ):
    return scored_individual[1]
def pick_best ( population, num_to_pick ):
    population.sort( key=get_score )
    return population[-num_to_pick:]

# how to do an optimization
def optimize_partition (
        initial_pool = None, # initial set of partitions to evolve
        size_of_partition = 5, # number of parts to create
        prob_mutate = 0.1, # prob for a new offspring to have a mutation
        births_per_generation = None, # how many breedings to do each generation
        num_generations = 1000, # how long to run the genetic algorithm for
        objective_function = None, # must provide this, maps partitions to floats
        progress_callback = None, # if you want a call every generation
        ):
    # how to attach/extract a score to/from an individual
    def with_score ( individual ):
        return ( individual, objective_function( individual ) )
    # how to produce a baby:
    # 1. breed the parents
    # 2. maybe apply mutation
    # 3. compute fitness score
    def make_baby ( parents ):
        baby = uniform_crossover( parents[0][0], parents[1][0] )
        mutate( baby, prob_mutate, size_of_partition - 1 )
        return with_score( baby )
    # use the initial population we were given, with fitness values added:
    population = [ with_score( individual ) for individual in initial_pool ]
    population.sort( key=get_score )
    # fill in default value(s):
    if births_per_generation == None:
        births_per_generation = len( initial_pool )
    # start timing
    start = time.time()
    # how to report pool progress
    def report_pool ( generation ):
        def write_time ( dt=None ):
            return '?????' if dt == None else str( datetime.timedelta( seconds = int( dt ) ) )[2:]
        elapsed = time.time() - start
        proportion_done = generation / num_generations
        time_left = None if proportion_done == 0 else ( 1 / proportion_done - 1 ) * elapsed
        print( 'After {:>5d} generations: max score = {:8.4f}   {:3d}% done, {}/{} ({})'.format(
            generation, max( map( get_score, population ) ), int( 100 * proportion_done ),
            write_time( elapsed ),
            write_time( None if time_left == None else elapsed + time_left ),
            write_time( time_left )
        ) )
    # reporting frequency
    freq = min( 100, max( 10, 10 * int( num_generations / 100 ) ) )
    # track best fitness in pool over time
    best_fitnesses = [ population[-1][1] ]
    # evolve it
    pool = pathos.pools.ProcessPool()
    for g in range( num_generations ):
        # report progress every so often
        if progress_callback != None:
            progress_callback( g, num_generations, get_score( population[-1] ) )
        else:
            if g % freq == 0:
                report_pool( g )
        
        # put the next generation into the pool
        breeders = [ random.sample( population, 2 ) for i in range( births_per_generation ) ]
        population += pool.map( make_baby, breeders )

        # apply survival of the fittest
        population[:] = pick_best( population, len( initial_pool ) )
        # record best fit
        best_fitnesses += [ population[-1][1] ]
    # print how good it is at the end
    report_pool( num_generations )
    # return best one in pool; this is the last, since pick_best just sored by fitness
    return population[-1][0], best_fitnesses
