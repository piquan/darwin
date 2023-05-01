#! /usr/bin/env python3

import random
import sys

import openai
import yaml

def main():
    if len(sys.argv) != 2:
        print("Usage: darwin.py config.yaml", file=sys.stderr)
        sys.exit(1)

    with open("openai_api_key", "r") as fh:
        openai.api_key = fh.read().strip()

    with open(sys.argv[1], "r") as fh:
        config = yaml.load(fh, Loader=yaml.Loader)
    messages = [{"role": "system", "content": config['sysmsg']}]
    prompt_fmt = config['prompt_fmt']
    training_pct = config['training_pct']

    testing = []
    for c in config['challenges']:
        prompt_msg = c[0]['content']
        if len(c) > 1 and random.randrange(100) < training_pct:
            messages += c
        else:
            testing.append(prompt_msg)

    try:
        for c in testing:
            messages.append({"role": "user",
                             "content": prompt_fmt.format(msg=c)})
            rsp = ""
            print(">>>", c)
            for chunk in openai.ChatCompletion.create(
                    messages=messages, model="gpt-3.5-turbo",
                    temperature=0, stream=True):
                chunk_message = chunk['choices'][0]['delta']
                if 'content' not in chunk_message:
                    continue
                print(chunk_message['content'], end='')
                sys.stdout.flush()
                rsp += chunk_message['content']
            print("\n")
            messages[-1]['content'] = c
            messages.append({"role": "assistant", "content": rsp})

    finally:
        print(yaml.dump(messages, width=64, allow_unicode=True))


if __name__ == "__main__":
    main()
