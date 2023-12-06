{
  description = "The Zcash Trailing Finality Layer Book";

  inputs.nixpkgs.url = "github:nixos/nixpkgs/23.11";

  outputs = { self, nixpkgs }:
  let
    system = "x86_64-linux";
    pkgs = nixpkgs.legacyPackages."${system}";

    tfl-book-pkg = pkgs.stdenv.mkDerivation rec {
      pname = "tfl-book";
      version = "0.1.0"; # BUG: This should be derived from the `git describe --dirty`

      buildInputs = with pkgs; [
        graphviz
        mdbook
        mdbook-graphviz
        mdbook-linkcheck
      ];

      src = ./.;

      builder = pkgs.writeScript "${pname}-builder-${version}" ''
        source "$stdenv/setup"
        cp -a "$src" ./src
        cd ./src
        chmod -R u+w .
        find "$(pwd)" -exec ls -ld '{}' \;
        dest="$out/share/doc/${pname}/${version}"
        mkdir -p "$dest"
        mdbook build --dest-dir="$dest/"
      '';
    };
  in {
    packages."${system}".default = tfl-book-pkg;
  };
}
