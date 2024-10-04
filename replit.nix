{pkgs}: {
  deps = [
    pkgs.file
    pkgs.pango
    pkgs.harfbuzz
    pkgs.glib
    pkgs.ghostscript
    pkgs.fontconfig
    pkgs.postgresql
  ];
}
