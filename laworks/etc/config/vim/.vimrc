"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
" This vimrc is based on the vimrc by Amix - http://amix.dk/
" You can find the latest version on:
"       http://blog.csdn.net/easwy
"
" Maintainer: Leo.C.Wu
" Version: 0.1
" Last Change: 31/05/07 09:17:57
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
" General
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
"Get out of VI's compatible mode..
set nocompatible

" Platform
function! MySys()
  return "linux"
endfunction

"Sets how many lines of history VIM har to remember
set history=400

" Chinese
if MySys() == "windows"
   "set encoding=utf-8
   "set langmenu=zh_CN.UTF-8
   "language message zh_CN.UTF-8
   "set fileencodings=ucs-bom,utf-8,gb18030,cp936,big5,euc-jp,euc-kr,latin1
endif

"Enable filetype plugin
filetype plugin on
filetype indent on

"Set to auto read when a file is changed from the outside
set autoread

"Have the mouse enabled all the time:
set mouse=v

"set cursor in the middle of screen
set scrolloff=7

"set cursor line
set cursorline

"Set mapleader
let mapleader = ","
let g:mapleader = ","

"Fast saving
nmap <silent> <leader>ww :w<cr>
nmap <silent> <leader>wf :w!<cr>

"Fast quiting
nmap <silent> <leader>qw :wq<cr>
nmap <silent> <leader>qf :q!<cr>
nmap <silent> <leader>qq :q<cr>
nmap <silent> <leader>qa :qa<cr>

"Fast remove highlight search
nmap <silent> <leader><cr> :noh<cr>

"Fast redraw
nmap <silent> <leader>rr :redraw!<cr>

" Switch to buffer according to file name
function! SwitchToBuf(filename)
    "let fullfn = substitute(a:filename, "^\\~/", $HOME . "/", "")
    " find in current tab
    let bufwinnr = bufwinnr(a:filename)
    if bufwinnr != -1
        exec bufwinnr . "wincmd w"
        return
    else
        " find in each tab
        tabfirst
        let tab = 1
        while tab <= tabpagenr("$")
            let bufwinnr = bufwinnr(a:filename)
            if bufwinnr != -1
                exec "normal " . tab . "gt"
                exec bufwinnr . "wincmd w"
                return
            endif
            tabnext
            let tab = tab + 1
        endwhile
        " not exist, new tab
        exec "tabnew " . a:filename
    endif
endfunction

"Fast edit vimrc
if MySys() == 'linux'
    "Fast reloading of the .vimrc
    map <silent> <leader>ss :source ~/.vimrc<cr>
    "Fast editing of .vimrc
    map <silent> <leader>ee :call SwitchToBuf("~/.vimrc")<cr>
    "When .vimrc is edited, reload it
    autocmd! bufwritepost .vimrc source ~/.vimrc
elseif MySys() == 'windows'
    " Set helplang
    set helplang=cn
    "Fast reloading of the _vimrc
    map <silent> <leader>ss :source ~/_vimrc<cr>
    "Fast editing of _vimrc
    map <silent> <leader>ee :call SwitchToBuf("~/_vimrc")<cr>
    "When _vimrc is edited, reload it
    autocmd! bufwritepost _vimrc source ~/_vimrc
    "Fast copying from linux
    func! CopyFromZ()
      autocmd! bufwritepost _vimrc
      exec 'split y:/.vimrc'
      exec 'normal 17G'
      exec 's/return "linux"/return "windows"/'
      exec 'w! ~/_vimrc'
      exec 'normal u'
      exec 'q'
    endfunc
    nnoremap <silent> <leader>uu :call CopyFromZ()<cr>:so ~/_vimrc<cr>
endif

" For windows version
if MySys() == 'windows'
    source $VIMRUNTIME/mswin.vim
    behave mswin

    set diffexpr=MyDiff()
    function! MyDiff()
        let opt = '-a --binary '
        if &diffopt =~ 'icase' | let opt = opt . '-i ' | endif
        if &diffopt =~ 'iwhite' | let opt = opt . '-b ' | endif
        let arg1 = v:fname_in
        if arg1 =~ ' ' | let arg1 = '"' . arg1 . '"' | endif
        let arg2 = v:fname_new
        if arg2 =~ ' ' | let arg2 = '"' . arg2 . '"' | endif
        let arg3 = v:fname_out
        if arg3 =~ ' ' | let arg3 = '"' . arg3 . '"' | endif
        let eq = ''
        if $VIMRUNTIME =~ ' '
            if &sh =~ '\<cmd'
                let cmd = '""' . $VIMRUNTIME . '\diff"'
                let eq = '"'
            else
                let cmd = substitute($VIMRUNTIME, ' ', '" ', '') . '\diff"'
            endif
        else
            let cmd = $VIMRUNTIME . '\diff'
        endif
        silent execute '!' . cmd . ' ' . opt . arg1 . ' ' . arg2 . ' > ' . arg3 . eq
    endfunction
endif

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
" Colors and Fonts
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

"Set font
"if MySys() == "linux"
"  set gfn=Monospace\ 11
"endif

" Avoid clearing hilight definition in plugins
if !exists("g:vimrc_loaded")
    "Enable syntax hl
    syntax enable

    " color scheme
    if has("gui_running")
        set guioptions-=T
        set guioptions-=m
        set guioptions-=L
        set guioptions-=r
        "hi normal guibg=#294d4a
    else
    endif " has
endif " exists(...)

"Some nice mapping to switch syntax (useful if one mixes different languages in one file)
map <leader>1 :set syntax=c<cr>
map <leader>2 :set syntax=xhtml<cr>
map <leader>3 :set syntax=python<cr>
map <leader>4 :set ft=javascript<cr>
map <leader>$ :syntax sync fromstart<cr>

autocmd BufEnter * :syntax sync fromstart

"Highlight current
"if has("gui_running")
"  set cursorline
"  hi cursorline guibg=#333333
"  hi CursorColumn guibg=#333333
"endif

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
" Fileformats
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
"Favorite filetypes
set ffs=unix,dos

nmap <leader>fd :se ff=dos<cr>
nmap <leader>fu :se ff=unix<cr>

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
" VIM userinterface
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
"Set 7 lines to the curors - when moving vertical..
"set so=7

" Maximum window when GUI running
if has("gui_running")
  set lines=9999
  set columns=9999
endif

"Turn on WiLd menu
set wildmenu

"Always show current position
set ruler

"The commandbar is 2 high
set cmdheight=2

"Show line number
set nu

"Do not redraw, when running macros.. lazyredraw
set lz

"Change buffer - without saving
"set hid

"Set backspace
set backspace=eol,start,indent

"Bbackspace and cursor keys wrap to
"set whichwrap+=<,>,h,l
set whichwrap+=<,>

"Ignore case when searching
set ignorecase

"Include search
set incsearch

"Highlight search things
set hlsearch

"Set magic on
set magic

"No sound on errors.
set noerrorbells
set novisualbell
set t_vb=

"show matching bracets
set showmatch

"How many tenths of a second to blink
set mat=2

  """"""""""""""""""""""""""""""
  " Statusline
  """"""""""""""""""""""""""""""
  "Always hide the statusline
  set laststatus=2

  function! CurDir()
     let curdir = substitute(getcwd(), '/home/leo/', "~/", "g")
     return curdir
  endfunction

  "Format the statusline
  "set statusline=\ %F%m%r%h\ %w\ \ CWD:\ %r%{CurDir()}%h\ \ \ Line:\ %l/%L:%c



""""""""""""""""""""""""""""""
" Visual
""""""""""""""""""""""""""""""
" From an idea by Michael Naumann
function! VisualSearch(direction) range
  let l:saved_reg = @"
  execute "normal! vgvy"
  let l:pattern = escape(@", '\\/.*$^~[]')
  let l:pattern = substitute(l:pattern, "\n$", "", "")
  if a:direction == 'b'
    execute "normal ?" . l:pattern . "^M"
  else
    execute "normal /" . l:pattern . "^M"
  endif
  let @/ = l:pattern
  let @" = l:saved_reg
endfunction

"Basically you press * or # to search for the current selection !! Really useful
vnoremap <silent> * :call VisualSearch('f')<CR>
vnoremap <silent> # :call VisualSearch('b')<CR>


"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
" Moving around and tabs
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
"Map space to / and c-space to ?
"map <space> /
"map <c-space> ?

"Smart way to move btw. windows
nmap <C-j> <C-W>j
nmap <C-k> <C-W>k
nmap <C-h> <C-W>h
nmap <C-l> <C-W>l

"Actually, the tab does not switch buffers, but my arrows
"Bclose function can be found in "Buffer related" section
map <leader>bd :Bclose<cr>
"map <down> <leader>bd

"Use the arrows to something usefull
"map <right> :bn<cr>
"map <left> :bp<cr>

"Tab configuration
map <leader>tn :tabnew
map <leader>te :tabedit
map <leader>tc :tabclose<cr>
map <leader>tm :tabmove
try
  set switchbuf=useopen
  set stal=1
catch
endtry

"Moving fast to front, back and 2 sides ;)
imap <m-$> <esc>$a
imap <m-0> <esc>0i

"Switch to current dir
map <silent> <leader>cd :cd %:p:h<cr>

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
" Parenthesis/bracket expanding
""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
vnoremap @1 <esc>`>a)<esc>`<i(<esc>
")
vnoremap @2 <esc>`>a]<esc>`<i[<esc>
vnoremap @3 <esc>`>a}<esc>`<i{<esc>
vnoremap @$ <esc>`>a"<esc>`<i"<esc>
vnoremap @q <esc>`>a'<esc>`<i'<esc>
vnoremap @w <esc>`>a"<esc>`<i"<esc>

"Map auto complete of (, ", ', [
inoremap @1 ()<esc>:let leavechar=")"<cr>i
inoremap @2 []<esc>:let leavechar="]"<cr>i
inoremap @3 {}<esc>:let leavechar="}"<cr>i
inoremap @4 {<esc>o}<esc>:let leavechar="}"<cr>O
inoremap @q ''<esc>:let leavechar="'"<cr>i
inoremap @w ""<esc>:let leavechar='"'<cr>i
"au BufNewFile,BufRead *.\(vim\)\@! inoremap " ""<esc>:let leavechar='"'<cr>i
"au BufNewFile,BufRead *.\(txt\)\@! inoremap ' ''<esc>:let leavechar="'"<cr>i

"imap <m-l> <esc>:exec "normal f" . leavechar<cr>a
"imap <d-l> <esc>:exec "normal f" . leavechar<cr>a


"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
" General Abbrevs
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
"My information
iab xdate <c-r>=strftime("%c")<cr>
iab xname Leo.C.Wu


"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
" Editing mappings etc.
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

func! DeleteTrailingWS()
  exe "normal mz"
  %s/\s\+$//ge
  nohl
  exe "normal `z"
endfunc

" do not automaticlly remove trailing whitespace
"autocmd BufWrite *.[ch] :call DeleteTrailingWS()
"autocmd BufWrite *.cc :call DeleteTrailingWS()
"autocmd BufWrite *.txt :call DeleteTrailingWS()
nmap <silent> <leader>ws :call DeleteTrailingWS()<cr>:w<cr>
"nmap <silent> <leader>ws! :call DeleteTrailingWS()<cr>:w!<cr>

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
" Command-line config
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
"Bash like
cnoremap <C-A>    <Home>
cnoremap <C-E>    <End>
cnoremap <C-K>    <C-U>

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
" Buffer realted
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
"Open a dummy buffer for paste
map <leader>es :tabnew<cr>:setl buftype=nofile<cr>
if MySys() == "linux"
map <leader>ec :tabnew ~/tmp/scratch.txt<cr>
else
map <leader>ec :tabnew $TEMP/scratch.txt<cr>
endif

"Restore cursor to file position in previous editing session
set viminfo='10,\"100,:20,n~/.viminfo
au BufReadPost * if line("'\"") > 0|if line("'\"") <= line("$")|exe("norm '\"")|else|exe "norm $"|endif|endif

" Don't close window, when deleting a buffer
command! Bclose call <SID>BufcloseCloseIt()

function! <SID>BufcloseCloseIt()
   let l:currentBufNum = bufnr("%")
   let l:alternateBufNum = bufnr("#")

   if buflisted(l:alternateBufNum)
     buffer #
   else
     bnext
   endif

   if bufnr("%") == l:currentBufNum
     new
   endif

   if buflisted(l:currentBufNum)
     execute("bdelete! ".l:currentBufNum)
   endif
endfunction

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
" Session options
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
set sessionoptions-=curdir
set sessionoptions+=sesdir

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
" Files and backups
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
"Turn backup off
set nobackup
set nowb
"set noswapfile


"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
" Folding
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
"Enable folding, I find it very useful
"set fen
"set fdl=0
nmap <silent> <leader>zo zO
vmap <silent> <leader>zo zO


"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
" Text options
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
set expandtab
set shiftwidth=4

map <leader>t2 :set shiftwidth=2<cr>
map <leader>t4 :set shiftwidth=4<cr>
au FileType html,python,vim,javascript,php setl shiftwidth=4
"au FileType html,python,vim,javascript setl tabstop=2
au FileType java,c setl shiftwidth=4
"au FileType java setl tabstop=4
au FileType txt setl lbr
au FileType txt setl tw=78

set smarttab
"set lbr
"set tw=78

   """"""""""""""""""""""""""""""
   " Indent
   """"""""""""""""""""""""""""""
   "Auto indent
   set ai

   "Smart indet
   set si

   "C-style indeting
   set cindent

   "Wrap lines
   set wrap


"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
" Spell checking
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
map <leader>sn ]s
map <leader>sp [s
map <leader>sa zg
map <leader>s? z=

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
" Complete
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
" options
set completeopt=menu
set complete-=u
set complete-=i

" mapping
inoremap <expr> <CR>       pumvisible()?"\<C-Y>":"\<CR>"
inoremap <expr> <C-J>      pumvisible()?"\<PageDown>\<C-N>\<C-P>":"\<C-X><C-O>"
inoremap <expr> <C-K>      pumvisible()?"\<PageUp>\<C-P>\<C-N>":"\<C-K>"
inoremap <expr> <C-U>      pumvisible()?"\<C-E>":"\<C-U>"
inoremap <C-]>             <C-X><C-]>
inoremap <C-F>             <C-X><C-F>
inoremap <C-D>             <C-X><C-D>
inoremap <C-L>             <C-X><C-L>

" Enable syntax
if has("autocmd") && exists("+omnifunc")
  autocmd Filetype *
        \if &omnifunc == "" |
        \  setlocal omnifunc=syntaxcomplete#Complete |
        \endif
endif

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
" cscope setting
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
if has("cscope")
  if MySys() == "linux"
    set csprg=/usr/bin/cscope
  else
    set csprg=cscope
  endif
  set csto=1
  set cst
  set nocsverb
  " add any database in current directory
  if filereadable("cscope.out")
      cs add cscope.out
  endif
  set csverb
endif

nmap <C-@>s :cs find s <C-R>=expand("<cword>")<CR><CR>
nmap <C-@>g :cs find g <C-R>=expand("<cword>")<CR><CR>
nmap <C-@>c :cs find c <C-R>=expand("<cword>")<CR><CR>
nmap <C-@>t :cs find t <C-R>=expand("<cword>")<CR><CR>
nmap <C-@>e :cs find e <C-R>=expand("<cword>")<CR><CR>
nmap <C-@>f :cs find f <C-R>=expand("<cfile>")<CR><CR>
nmap <C-@>i :cs find i ^<C-R>=expand("<cfile>")<CR>$<CR>
nmap <C-@>d :cs find d <C-R>=expand("<cword>")<CR><CR>

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
" Plugin configuration
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
   """"""""""""""""""""""""""""""
   " Super Tab
   """"""""""""""""""""""""""""""
   "let g:SuperTabDefaultCompletionType = "<C-X><C-O>"
   let g:SuperTabDefaultCompletionType = "<C-P>"

   """"""""""""""""""""""""""""""
   " yank ring setting
   """"""""""""""""""""""""""""""
   map <leader>yr :YRShow<cr>

   """"""""""""""""""""""""""""""
   " file explorer setting
   """"""""""""""""""""""""""""""
   "Split vertically
   let g:explVertical=1

   "Window size
   let g:explWinSize=35

   let g:explSplitLeft=1
   let g:explSplitBelow=1

   "Hide some files
   let g:explHideFiles='^\.,.*\.class$,.*\.swp$,.*\.pyc$,.*\.swo$,\.DS_Store$'

   "Hide the help thing..
   let g:explDetailedHelp=0


   """"""""""""""""""""""""""""""
   " minibuffer setting
   """"""""""""""""""""""""""""""
   let loaded_minibufexplorer = 1         " *** Disable minibuffer plugin
   let g:miniBufExplorerMoreThanOne = 2   " Display when more than 2 buffers
   let g:miniBufExplSplitToEdge = 1       " Always at top
   let g:miniBufExplMaxSize = 3           " The max height is 3 lines
   let g:miniBufExplMapWindowNavVim = 1   " map CTRL-[hjkl]
   let g:miniBufExplUseSingleClick = 1    " select by single click
   let g:miniBufExplModSelTarget = 1      " Dont change to unmodified buffer
   let g:miniBufExplForceSyntaxEnable = 1 " force syntax on
   "let g:miniBufExplVSplit = 25
   "let g:miniBufExplSplitBelow = 0

   autocmd BufRead,BufNew :call UMiniBufExplorer

   """"""""""""""""""""""""""""""
   " bufexplorer setting
   """"""""""""""""""""""""""""""
   let g:bufExplorerDefaultHelp=1       " Do not show default help.
   let g:bufExplorerShowRelativePath=1  " Show relative paths.
   let g:bufExplorerSortBy='mru'        " Sort by most recently used.
   let g:bufExplorerSplitRight=0        " Split left.
   let g:bufExplorerSplitVertical=1     " Split vertically.
   let g:bufExplorerSplitVertSize = 30  " Split width
   let g:bufExplorerUseCurrentWindow=1  " Open in new window.
   let g:bufExplorerMaxHeight=13        " Max height

   """"""""""""""""""""""""""""""
   " taglist setting
   """"""""""""""""""""""""""""""
   if MySys() == "windows"
     let Tlist_Ctags_Cmd = 'ctags'
   elseif MySys() == "linux"
     let Tlist_Ctags_Cmd = '/usr/bin/ctags'
   endif
   let Tlist_Show_One_File = 1
   let Tlist_Exit_OnlyWindow = 1
   let Tlist_Use_Right_Window = 1
   nmap <silent> <leader>tl :Tlist<cr>

   """"""""""""""""""""""""""""""
   " winmanager setting
   """"""""""""""""""""""""""""""
   let g:winManagerWindowLayout = "BufExplorer,FileExplorer|TagList"
   let g:winManagerWidth = 30
   let g:defaultExplorer = 0
   nmap <C-W><C-F> :FirstExplorerWindow<cr>
   nmap <C-W><C-B> :BottomExplorerWindow<cr>
   nmap <silent> <leader>wm :WMToggle<cr>
   autocmd BufWinEnter \[Buf\ List\] setl nonumber

   """"""""""""""""""""""""""""""
   " netrw setting
   """"""""""""""""""""""""""""""
   let g:netrw_winsize = 30
   nmap <silent> <leader>fe :Sexplore!<cr>

   """"""""""""""""""""""""""""""
   " LaTeX Suite things
   """"""""""""""""""""""""""""""
   set grepprg=grep\ -nH\ $*
   let g:Tex_DefaultTargetFormat="pdf"
   let g:Tex_ViewRule_pdf='xpdf'

   "Bindings
   autocmd FileType tex map <silent><leader><space> :w!<cr> :silent! call Tex_RunLaTeX()<cr>

   "Auto complete some things ;)
   autocmd FileType tex inoremap $i \indent
   autocmd FileType tex inoremap $* \cdot
   autocmd FileType tex inoremap $i \item
   autocmd FileType tex inoremap $m \[<cr>\]<esc>O


   """"""""""""""""""""""""""""""
   " lookupfile setting
   """"""""""""""""""""""""""""""
   let g:LookupFile_MinPatLength = 2
   let g:LookupFile_PreserveLastPattern = 0
   let g:LookupFile_PreservePatternHistory = 0
   let g:LookupFile_AlwaysAcceptFirst = 1
   let g:LookupFile_AllowNewFiles = 0
   if filereadable("./filenametags")
       let g:LookupFile_TagExpr = '"./filenametags"'
   endif
   nmap <silent> <leader>lk <Plug>LookupFile<cr>
   nmap <silent> <leader>ll :LUBufs<cr>
   nmap <silent> <leader>lw :LUWalk<cr>

   " lookup file with ignore case
   function! LookupFile_IgnoreCaseFunc(pattern)
       let _tags = &tags
       try
           let &tags = eval(g:LookupFile_TagExpr)
           let newpattern = '\c' . a:pattern
           let tags = taglist(newpattern)
       catch
           echohl ErrorMsg | echo "Exception: " . v:exception | echohl NONE
           return ""
       finally
           let &tags = _tags
       endtry

       " Show the matches for what is typed so far.
       let files = map(tags, 'v:val["filename"]')
       return files
   endfunction
   let g:LookupFile_LookupFunc = 'LookupFile_IgnoreCaseFunc'

   """"""""""""""""""""""""""""""
   " markbrowser setting
   """"""""""""""""""""""""""""""
   nmap <silent> <leader>mk :MarksBrowser<cr>

   """"""""""""""""""""""""""""""
   " showmarks setting
   """"""""""""""""""""""""""""""
   " Enable ShowMarks
   let showmarks_enable = 1
   " Show which marks
   let showmarks_include = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
   " Ignore help, quickfix, non-modifiable buffers
   let showmarks_ignore_type = "hqm"
   " Hilight lower & upper marks
   let showmarks_hlline_lower = 1
   let showmarks_hlline_upper = 1

   """"""""""""""""""""""""""""""
   " mark setting
   """"""""""""""""""""""""""""""
   nmap <silent> <leader>hl <Plug>MarkSet
   vmap <silent> <leader>hl <Plug>MarkSet
   nmap <silent> <leader>hh <Plug>MarkClear
   vmap <silent> <leader>hh <Plug>MarkClear
   nmap <silent> <leader>hr <Plug>MarkRegex
   vmap <silent> <leader>hr <Plug>MarkRegex

   """"""""""""""""""""""""""""""
   " FeralToggleCommentify setting
   """"""""""""""""""""""""""""""
   let loaded_feraltogglecommentify = 1
   "map <silent> <leader>tc :call ToggleCommentify()<CR>j
   "imap <M-c> <ESC>:call ToggleCommentify()<CR>j

   """"""""""""""""""""""""""""""
   " vimgdb setting
   """"""""""""""""""""""""""""""
   let g:vimgdb_debug_file = ""
   run macros/gdb_mappings.vim

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
" Filetype generic
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
   """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
   " Todo
   """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
   "au BufNewFile,BufRead *.todo so ~/vim_local/syntax/amido.vim

   """"""""""""""""""""""""""""""
   " HTML related
   """"""""""""""""""""""""""""""
   " HTML entities - used by xml edit plugin
   let xml_use_xhtml = 1
   "let xml_no_auto_nesting = 1

   "To HTML
   let html_use_css = 1
   let html_number_lines = 0
   let use_xhtml = 1

   """""""""""""""""""""""""""""""
   " Vim section
   """""""""""""""""""""""""""""""
   autocmd FileType vim set nofen
   autocmd FileType vim map <buffer> <leader><space> :w!<cr>:source %<cr>

   """"""""""""""""""""""""""""""
   " HTML
   """""""""""""""""""""""""""""""
   au FileType html set ft=xml
   au FileType html set syntax=html


   """"""""""""""""""""""""""""""
   " C/C++
   """""""""""""""""""""""""""""""
   autocmd FileType c,cpp  map <buffer> <leader><space> :make<cr>
   "autocmd FileType c,cpp  setl foldmethod=syntax | setl fen

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
" MISC
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
   "Quickfix
   nmap <leader>cn :cn<cr>
   nmap <leader>cp :cp<cr>
   nmap <leader>cw :cw 10<cr>
   "nmap <leader>cc :botright lw 10<cr>
   "map <c-u> <c-l><c-j>:q<cr>:botright cw 10<cr>

   function! s:GetVisualSelection()
       let save_a = @a
       silent normal! gv"ay
       let v = @a
       let @a = save_a
       let var = escape(v, '\\/.$*')
       return var
   endfunction

   " Fast grep
   nmap <silent> <leader>lv :lv /<c-r>=expand("<cword>")<cr>/ %<cr>:lw<cr>
   vmap <silent> <leader>lv :lv /<c-r>=<sid>GetVisualSelection()<cr>/ %<cr>:lw<cr>

   " Fast diff
   cmap @vd vertical diffsplit
   set diffopt+=vertical

   "Remove the Windows ^M
   noremap <Leader>dm mmHmn:%s/<C-V><cr>//ge<cr>'nzt'm

   "Paste toggle - when pasting something in, don't indent.
   set pastetoggle=<F3>

   "Remove indenting on empty lines
   "map <F2> :%s/\s*$//g<cr>:noh<cr>''

   "Super paste
   "inoremap <C-v> <esc>:set paste<cr>mui<C-R>+<esc>mv'uV'v=:set nopaste<cr>

   "Fast Ex command
   nnoremap ; :

   "For mark move
   nnoremap <leader>' '

   "Fast copy
   nnoremap ' "

   "A function that inserts links & anchors on a TOhtml export.
   " Notice:
   " Syntax used is:
   " Link
   " Anchor
   function! SmartTOHtml()
    TOhtml
    try
     %s/&quot;\s\+\*&gt; \(.\+\)</" <a href="#\1" style="color: cyan">\1<\/a></g
     %s/&quot;\(-\|\s\)\+\*&gt; \(.\+\)</" \&nbsp;\&nbsp; <a href="#\2" style="color: cyan;">\2<\/a></g
     %s/&quot;\s\+=&gt; \(.\+\)</" <a name="\1" style="color: #fff">\1<\/a></g
    catch
    endtry
    exe ":write!"
    exe ":bd"
   endfunction


""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
" Mark as loaded
""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
let g:vimrc_loaded = 1
nmap <F8> :TagbarToggle<CR> 
