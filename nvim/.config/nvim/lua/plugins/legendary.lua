return {
  {
    "stevearc/dressing.nvim",
    opts = {
      select = {
        backend = { "telescope" },
      },
    },
  },
  {
    "mrjones2014/legendary.nvim",
    priority = 10000,
    lazy = false,
    dependencies = {
      "nvim-telescope/telescope.nvim",
      "stevearc/dressing.nvim",
      "kkharji/sqlite.lua",
    },
    opts = {
      extensions = {
        lazy_nvim = true,
      },
      sort = {
        frecency = {
          db_root = vim.fn.stdpath("data"),
          max_timestamps = 10,
        },
      },
      commands = {
        { ":Format", description = "Format current buffer" },
        { ":Lazy", description = "Open Lazy plugin manager" },
        { ":Mason", description = "Open Mason LSP installer" },
      },
      keymaps = {
        {
          "<leader>p",
          ":Legendary<CR>",
          description = "Open command palette",
          mode = { "n", "i", "v" },
        },
        {
          "<C-s>",
          ":w<CR>",
          description = "Save file",
          mode = { "n", "i", "v" },
        },
      },
    },
  },
}
