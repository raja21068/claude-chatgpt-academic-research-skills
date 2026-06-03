# Local Helper Tools

These scripts are optional.

They do not use an OpenAI API key.
They do not use Gmail API.
They do not send emails.

They only help organize ChatGPT-generated batch files.

## 1. Validate professors.csv

```bash
python local_tools/validate_professors_csv.py examples/batch_example/professors/professors.csv
```

## 2. Create send queue and .eml files

```bash
python local_tools/make_send_queue.py examples/batch_example
```

This creates:

```text
examples/batch_example/send_queue/send_queue.csv
examples/batch_example/send_queue/send_queue.html
examples/batch_example/emails_eml/*.eml
```

## 3. Build ZIP

```bash
python local_tools/build_batch_zip.py examples/batch_example
```

This creates:

```text
examples/batch_example.zip
```
