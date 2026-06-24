// Copyright (C) 2023-2026 Bank Statement Parser. All rights reserved.
// Licensed under the Apache License, Version 2.0.
//
// VS Code client that launches the `bankstatementparser-lsp` language server
// (stdio) for MT940 bank-statement files (.mt940 / .sta). The server itself
// lives in Python: `pip install bankstatementparser-lsp`. It shares the MT940
// tag patterns the core parser relies on, so the editor never disagrees with
// the rest of the toolchain.

import { workspace, ExtensionContext } from "vscode";
import {
  LanguageClient,
  LanguageClientOptions,
  ServerOptions,
  TransportKind,
} from "vscode-languageclient/node";

let client: LanguageClient;

export function activate(_context: ExtensionContext): void {
  const config = workspace.getConfiguration("bankstatementparser");
  const command = config.get<string>("serverCommand", "bankstatementparser-lsp");

  const serverOptions: ServerOptions = {
    command,
    transport: TransportKind.stdio,
  };

  const clientOptions: LanguageClientOptions = {
    documentSelector: [{ scheme: "file", language: "mt940" }],
    synchronize: {
      configurationSection: "bankstatementparser",
    },
  };

  client = new LanguageClient(
    "bankstatementparser-mt940",
    "BankStatementParser MT940 Language Server",
    serverOptions,
    clientOptions,
  );
  client.start();
}

export function deactivate(): Thenable<void> | undefined {
  return client ? client.stop() : undefined;
}
