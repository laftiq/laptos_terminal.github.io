(() => {
  const profiles = {
    pc: {
      user: "laptos@laptos",
      logo: [
        "       _,met$$$$$gg.",
        "    ,g$$$$$$$$$$$$$$$P.",
        '  ,g$$P"     """Y$$.".',
        " ,$$P'              `$$$.",
        "',$$P       ,ggs.     `$$b:",
        "`d$$'     ,$P\"'   .    $$$",
        " $$P      d$'     ,    $$P",
        " $$:      $$.   -    ,d$$'",
        " $$;      Y$b._   _,d$P'",
        ' Y$$.    `.`"Y$$$$P"\'',
        ' `$$b      "-.__',
        "  `Y$$",
        "   `Y$$.",
        "     `$$b.",
        "       `Y$$b.",
        '          `"Y$b._',
        '              `"""',
      ].join("\n"),
      specs: [
        ["system", "Debian GNU/Linux 13 (trixie) x86_64"],
        ["kernel", "Linux 6.12.113+deb13-amd64"],
        ["desktop", "Openbox (X11)"],
        ["terminal", "kitty 0.41.1"],
        ["shell", "zsh 5.9"],
        ["cpu", "AMD Ryzen 5 5600X (12) @ 4.65 GHz"],
        ["gpu", "NVIDIA GeForce RTX 4070 [Discrete]"],
        ["memory", "15.53 GiB"],
        ["disk", "47.93 GiB"],
      ],
    },
    homelab: {
      user: "root@pve",
      logo: [
        "  .://:.            .://:.",
        "`hMMMMMMd/        /dMMMMMMh`",
        " `sMMMMMMMd:    :dMMMMMMMs`",
        "   /mMMMMMMMy..yMMMMMMMm/",
        "    .hMMMMMMMMMMMMMMh.",
        "      +NMMMMMMMMMMN+",
        "    .hMMMMMMMMMMMMMMh.",
        "   /mMMMMMMMy..yMMMMMMMm/",
        " `sMMMMMMMd:    :dMMMMMMMs`",
        "`hMMMMMMd/        /dMMMMMMh`",
        "  `://:`            `://:`",
      ].join("\n"),
      specs: [
        ["system", "Proxmox VE 9.1.2 x86_64"],
        ["kernel", "Linux 6.17.2-2-pve"],
        ["desktop", "—"],
        ["terminal", "termproxy"],
        ["shell", "bash 5.2.37"],
        ["cpu", "Intel Core i3-3220 (4) @ 3.30 GHz"],
        ["gpu", "Intel E3-1200 v2 / 3rd Gen Core graphics"],
        ["memory", "15.50 GiB"],
        ["disk", "93.93 GiB · ext4"],
      ],
    },
  };
  const buttons = document.querySelectorAll("button[data-host]");
  const logo = document.getElementById("fetch-logo");
  const user = document.getElementById("fetch-user");
  const specs = document.getElementById("fetch-specs");

  function setHost(host) {
    const profile = profiles[host];
    logo.textContent = profile.logo;
    logo.dataset.host = host;
    user.textContent = profile.user;
    specs.replaceChildren();
    profile.specs.forEach(([key, value]) => {
      const dt = document.createElement("dt"),
        dd = document.createElement("dd");
      dt.textContent = key;
      dd.textContent = value;
      specs.append(dt, dd);
    });
    buttons.forEach((button) => {
      button.setAttribute("aria-pressed", String(button.dataset.host === host));
    });
  }
  buttons.forEach((button) => {
    button.addEventListener("click", () => setHost(button.dataset.host));
  });
  setHost("pc");
})();
