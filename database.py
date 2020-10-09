
import argparse
import datatable as dt
import cov_dates as cd
from math import nan
import dateutil.parser
import os
import pm_util as pmu
from dateutil.parser import parse

def cval(tableCell):
    return tableCell.to_list()[0][0]

def cstr(tableCell):
    return str(tableCell.to_list()[0][0])

def cint(tableCell):
    return int(tableCell.to_list()[0][0])

def analyzeDay(fullTable, day):
    dayTable = fullTable[(dt.f.DatenstandTag == day),:]
    cases = dayTable[(dt.f.NeuerFall == 0) | (dt.f.NeuerFall == 1), 'AnzahlFall'].sum()[0, 0]
    new_cases = dayTable[(dt.f.NeuerFall == -1) | (dt.f.NeuerFall == 1), 'AnzahlFall'].sum()[0, 0]
    dead = dayTable[(dt.f.NeuerTodesfall == 0) | (dt.f.NeuerTodesfall == 1), 'AnzahlTodesfall'].sum()[0, 0]
    new_dead = dayTable[(dt.f.NeuerTodesfall == -1) | (dt.f.NeuerTodesfall == 1), 'AnzahlTodesfall'].sum()[0, 0]

    recovered = 0
    new_recovered = 0
    if "NeuGenesen" in dayTable.keys():
        recovered = dayTable[(dt.f.NeuGenesen == 0) | (dt.f.NeuGenesen == 1), 'AnzahlGenesen'].sum()[0, 0]
        new_recovered = dayTable[(dt.f.NeuGenesen == -1) | (dt.f.NeuGenesen == 1), 'AnzahlGenesen'].sum()[0, 0]
    #lastDay=fullTable[:,'MeldeDay'].max()[0,0]
    #lastnewCaseOnDay=fullTable[:,'newCaseOnDay'].max()[0,0]
    print("{} Day {}: cases {} (+{}), dead {} (+{}), recovered {} (+{})".format(
        cd.dateStrDMFromDay(day), day, int(cases), int(new_cases), int(dead), int(new_dead), int(recovered),int(new_recovered)))

def analyzeDayRange(fullTable, fromDay, toDay):
    dayTable = fullTable[(dt.f.DatenstandTag >= fromDay) & (dt.f.DatenstandTag < toDay),:]

    cases_to_count = dayTable[(dt.f.NeuerFall == 0) | (dt.f.NeuerFall == 1),:]
    cases = cases_to_count[:, [dt.sum(dt.f.AnzahlFall)],dt.by(dt.f.DatenstandTag)]

    new_cases_to_count = dayTable[(dt.f.NeuerFall == -1) | (dt.f.NeuerFall == 1),:]
    new_cases = new_cases_to_count[:, [dt.sum(dt.f.AnzahlFall)],dt.by(dt.f.DatenstandTag)]

    dead_to_count = dayTable[(dt.f.NeuerTodesfall == 0) | (dt.f.NeuerTodesfall == 1),:]
    dead = dead_to_count[:, [dt.sum(dt.f.AnzahlTodesfall)],dt.by(dt.f.DatenstandTag)]

    new_dead_to_count = dayTable[(dt.f.NeuerTodesfall == -1) | (dt.f.NeuerTodesfall == 1),:]
    new_dead = new_dead_to_count[:, [dt.sum(dt.f.AnzahlTodesfall)],dt.by(dt.f.DatenstandTag)]

    if "NeuGenesen" in dayTable.keys():
        recovered_to_count = dayTable[(dt.f.NeuGenesen == 0) | (dt.f.NeuGenesen == 1),:]
        recovered = recovered_to_count[:, [dt.sum(dt.f.AnzahlGenesen)],dt.by(dt.f.DatenstandTag)]
        new_recovered_to_count = dayTable[(dt.f.NeuGenesen == -1) | (dt.f.NeuGenesen == 1),:]
        new_recovered = new_recovered_to_count[:, [dt.sum(dt.f.AnzahlGenesen)],dt.by(dt.f.DatenstandTag)]
    #lastDay=fullTable[:,'MeldeDay'].max()[0,0]
    #lastnewCaseOnDay=fullTable[:,'newCaseOnDay'].max()[0,0]
    print("From {}-{} Day {}-{}: cases {} (+{}), dead {} (+{}), recovered {} (+{})".format(
        cd.dateStrDMFromDay(fromDay), cd.dateStrDMFromDay(toDay), fromDay, toDay,
        cases.to_list(), new_cases.to_list(), dead.to_list(), new_dead.to_list(), recovered.to_list(), new_recovered.to_list()))
    return cases, new_cases, dead, new_dead, recovered, new_recovered


#def analyzeDayRangeBy(fullTable, fromDay, toDay, forIdLandkreis):
def analyzeDaily(fullTable, filter):

    #dayTable = fullTable[(dt.f.DatenstandTag >= fromDay) & (dt.f.DatenstandTag < toDay) & (dt.f.IdLandkreis == forIdLandkreis),:]
    dayTable = fullTable[filter,:]

    cases_to_count = dayTable[(dt.f.NeuerFall == 0) | (dt.f.NeuerFall == 1),:]
    cases = cases_to_count[:, [dt.sum(dt.f.AnzahlFall)],dt.by(dt.f.DatenstandTag)]
    cases.names = ["DatenstandTag", "AnzahlFall"]
    cases.key = "DatenstandTag"
    print("cases rows = {}".format(cases.nrows))
    print(cases)

    new_cases_to_count = dayTable[(dt.f.NeuerFall == -1) | (dt.f.NeuerFall == 1),:]
    new_cases = new_cases_to_count[:, [dt.sum(dt.f.AnzahlFall)],dt.by(dt.f.DatenstandTag)]
    new_cases.names = ["DatenstandTag", "AnzahlFallNeu"]
    new_cases.key = "DatenstandTag"
    print("new_cases rows = {}".format(new_cases.nrows))

    dead_to_count = dayTable[(dt.f.NeuerTodesfall == 0) | (dt.f.NeuerTodesfall == 1),:]
    dead = dead_to_count[:, [dt.sum(dt.f.AnzahlTodesfall)],dt.by(dt.f.DatenstandTag)]
    dead.names = ["DatenstandTag", "AnzahlTodesfall"]
    dead.key = "DatenstandTag"
    print("dead rows = {}".format(dead.nrows))

    new_dead_to_count = dayTable[(dt.f.NeuerTodesfall == -1) | (dt.f.NeuerTodesfall == 1),:]
    new_dead = new_dead_to_count[:, [dt.sum(dt.f.AnzahlTodesfall)],dt.by(dt.f.DatenstandTag)]
    new_dead.names = ["DatenstandTag", "AnzahlTodesfallNeu"]
    new_dead.key = "DatenstandTag"
    print("new_dead rows = {}".format(new_dead.nrows))

    recovered_to_count = dayTable[(dt.f.NeuGenesen == 0) | (dt.f.NeuGenesen == 1),:]
    recovered = recovered_to_count[:, [dt.sum(dt.f.AnzahlGenesen)],dt.by(dt.f.DatenstandTag)]
    recovered.names = ["DatenstandTag", "AnzahlGenesen"]
    recovered.key = "DatenstandTag"
    print("recovered rows = {}".format(recovered.nrows))

    new_recovered_to_count = dayTable[(dt.f.NeuGenesen == -1) | (dt.f.NeuGenesen == 1),:]
    new_recovered = new_recovered_to_count[:, [dt.sum(dt.f.AnzahlGenesen)],dt.by(dt.f.DatenstandTag)]
    new_recovered.names = ["DatenstandTag", "AnzahlGenesenNeu"]
    new_recovered.key = "DatenstandTag"
    print("new_recovered rows = {}".format(new_recovered.nrows))

    byDayTable = cases[:,:,dt.join(new_cases)][:,:,dt.join(dead)][:,:,dt.join(new_dead)][:,:,dt.join(recovered)][:,:,dt.join(new_recovered)]
    print("byDayTable rows = {}".format(byDayTable.nrows))
    #print(byDayTable)

    return byDayTable

def filterByDayAndLandkreis(fromDay, toDay, forIdLandkreis):
    return (dt.f.DatenstandTag >= fromDay) & (dt.f.DatenstandTag < toDay) & (dt.f.IdLandkreis == forIdLandkreis)

def filterByDayAndCriteria(fromDay, toDay, criteria):
    return (dt.f.DatenstandTag >= fromDay) & (dt.f.DatenstandTag < toDay) & criteria

def filterByDay(fromDay, toDay):
    return (dt.f.DatenstandTag >= fromDay) & (dt.f.DatenstandTag < toDay)

def timeSeries(fullTable, fromDay, toDay, byCriteria, nameColumn):
    regions = fullTable[:, [dt.first(nameColumn)], dt.by(byCriteria)]
    #regions = regions[:5,:]
    print("regions")
    print(regions)
    dailysByCriteria = {}
    for i, lk in enumerate(regions[:, byCriteria].to_list()[0]):
        dailysByCriteria[lk] = analyzeDaily(fullTable,
            filterByDayAndCriteria(fromDay, toDay, (byCriteria == lk)))
        print("Done {} of {}, key = {} name = {}".format(i+1, regions.nrows, lk, regions[i,nameColumn][0,0]))
    return regions, dailysByCriteria


def analyze(fullTable, args):
    print("Analyzing")
    print("Keys:")
    print(fullTable.keys())
    firstDumpDay = cint(fullTable[:,"DatenstandTag"].min())
    lastDumpDay = cint(fullTable[:,"DatenstandTag"].max())
    print("firstDumpDay", firstDumpDay)
    print("lastDumpDay",lastDumpDay)

    #fromDay = lastDumpDay-27
    fromDay = firstDumpDay
    toDay = lastDumpDay+1

    deutschland = analyzeDaily(fullTable, filterByDay(fromDay, toDay))
    print(deutschland)
    pmu.saveCsvTable(deutschland, "series-{}-{}-{}-{}.csv".format(firstDumpDay, lastDumpDay, 0, "Deutschland"), args.outputDir)

    bundeslaender, bundeslaender_numbers = timeSeries(fullTable, fromDay, toDay, dt.f.IdBundesland, dt.f.Bundesland)
    for i in range(bundeslaender.nrows):
        bl_name=bundeslaender[i,dt.f.Bundesland].to_list()[0][0]
        bl_id=bundeslaender[i,dt.f.IdBundesland].to_list()[0][0]
        #print(i)
        #print(bl_id)
        #print(bl_name)
        #print(bundeslaender_numbers[i+1])
        pmu.saveCsvTable(bundeslaender_numbers[bl_id], "series-{}-{}-{}-{}.csv".format(firstDumpDay, lastDumpDay, bl_id, bl_name), args.outputDir)

    landKreise, landkreise_numbers = timeSeries(fullTable, fromDay, toDay, dt.f.IdLandkreis, dt.f.Landkreis)
    print(landKreise)
    print(landkreise_numbers)
    for i in range(landKreise.nrows):
        print(i)
        lk_name = landKreise[i, dt.f.Landkreis].to_list()[0][0]
        lk_id = landKreise[i, dt.f.IdLandkreis].to_list()[0][0]
        pmu.saveCsvTable(landkreise_numbers[lk_id],
                         "series-{}-{}-{}-{}.csv".format(firstDumpDay, lastDumpDay, lk_id, lk_name), args.outputDir)
    #print(landKreise)

    return fullTable

def main():
    parser = argparse.ArgumentParser(description='Fast queries on all data')
    parser.add_argument('file', metavar='fileName', type=str, nargs='?',
                        help='.Full unified NPGEO COVID19 Germany data as .csv or .jay file',
                        default="archive_v2/all-data.jay")
    parser.add_argument('-d', '--output-dir', dest='outputDir', default="series")

    args = parser.parse_args()
    #print(args)
    print("Loading " + args.file)
    fullTable = dt.fread(args.file)
    print("Loading done loading table from ‘" + args.file + "‘")
    analyze(fullTable, args)

if __name__ == "__main__":
    # execute only if run as a script
    main()