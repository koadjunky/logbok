import argparse
import pendulum
import re


def parse_arguments():
    parser = argparse.ArgumentParser(description="Process logbok file")
    parser.add_argument('filename', help="file to process")
    args = parser.parse_args()
    return args.filename


def parse_file(fname):
    with open(fname, 'r') as f:
        for line in f:
            (tstamp, proc, title) = line.split(" ", 2)
            tstampi = 900 * (int(tstamp) // 900)
            proc = re.sub('.*/', '', proc)
            yield (tstampi, proc, title)


def start_day_timestamp(tstamp):
    date = pendulum.from_timestamp(tstamp, tz="Europe/Warsaw")
    start = date.start_of("day")
    return start.int_timestamp


def main():
    fname = parse_arguments()
    result = {}
    for (tstamp, proc, title) in parse_file(fname):
        if not result:
            date_start = start_day_timestamp(tstamp)
            for i in range(96):
                result[date_start + 900*i] = {}
        if tstamp not in result:
            date = pendulum.from_timestamp(tstamp, tz="Europe/Warsaw")
            raise Exception("Unknown timestamp " + str(date))
        key = (proc, title)
        if key not in result[tstamp]:
            result[tstamp][key] = 1
        else:
            result[tstamp][key] += 1
    for d, p in sorted(result.items()):
        date = pendulum.from_timestamp(d, tz="Europe/Warsaw")
        print(date)
        for k, v in sorted(p.items(), key=lambda item: item[1], reverse=True):
            print(v, k)
        print()


if __name__ == '__main__':
    main()
