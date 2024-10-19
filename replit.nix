{pkgs}: {
  deps = [
    pkgs.glibcLocales
    pkgs.freetype
    pkgs.file
    pkgs.pango
    pkgs.harfbuzz
    pkgs.glib
    pkgs.ghostscript
    pkgs.fontconfig
    pkgs.postgresql
  ];
}
