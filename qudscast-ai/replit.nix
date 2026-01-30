{ pkgs }: {
  deps = [
    pkgs.nodejs_20
    pkgs.nodePackages.npm
    pkgs.ffmpeg
    pkgs.python311
    pkgs.python311Packages.pip
    pkgs.python311Packages.gtts
    pkgs.espeak-ng
    pkgs.libuuid
  ];

  env = {
    LD_LIBRARY_PATH = pkgs.lib.makeLibraryPath [
      pkgs.libuuid
    ];
  };
}
