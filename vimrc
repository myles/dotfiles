filetype on
filetype plugin on
filetype indent on

" Variables
set softtabstop=4
set ignorecase
set number
nnoremap <F2> :set nonumber!<CR>:set foldcolumn=0<CR>

" Syntax Highlighting
set background=light
syntax enable

" Markdown filetype file
augroup markdown
    au! BufRead,BufNewFile *.mdown setfiletype mkd
augroup END
filetype plugin indent on
syntax on
