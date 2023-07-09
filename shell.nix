{ pkgs ? import <nixpkgs> { } }:
with pkgs;
let pythonEnv = python3.withPackages (ps: [ ps.scrapy ]);
in mkShell { packages = [ pythonEnv ]; }
