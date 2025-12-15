def bmain():
    print("htmlparser bmain")


def amain():
    input_file_path = None
    input_file = sys.argv[1] if len(sys.argv) > 1 else None

    cmd_file = sys.argv[1] if len(sys.argv) > 1 else "cmd.yaml"
    cmd_file_path = Path(cmd_file)
    top_config = TopConfig(cmd_file_path)
    env = top_config.get_env()
    patterns = top_config.get_patterns()

    if input_file is None:
        input_file = top_config.get_input_file_name() 

    if input_file is not None:
        input_file_path = Path(input_file)     

    app = App()
    if input_file_path is not None and input_file_path.exists():
        input_assoc = Util.load_yaml(input_file_path)
        app.links_assoc.update(input_assoc)

    for pattern in patterns:
        print("app.py main pattern={pattern}")
        ret = env.set_pattern(pattern)
        if ret is None:
            print(f"Not found pattern={pattern}")
            exit(0)
        app.run(env)

    output_file = top_config.get_output_file_name()
    print(f'output_file={output_file}')
    output_path = Path(output_file)
    Util.output_yaml(app.links_assoc, output_path)
    
    return 100
