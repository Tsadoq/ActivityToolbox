from activitytoolbox.activity.parsers.tcx_parser import load_tcx


def main():
    out = load_tcx(file_path="activity_21122573889.tcx")
    print(out)


if __name__ == "__main__":
    main()
