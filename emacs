;;;
;;; Org Mode
;;;
(setq load-path (cons "/usr/local/share/emacs/site-lisp" load-path))
(add-to-list 'load-path (expand-file-name "~/Dropbox/MobileOrg"))
(add-to-list 'auto-mode-alist '("\\.\\(org\\|org_archive\\|txt\\)$" . org-mode))
(require 'org-install)
;;
;; Sandard key bindings
;;
(global-set-key "\C-cl" 'org-store-link)
(global-set-key "\C-ca" 'org-agenda)
(global-set-key "\C-cc" 'org-capture)
(global-set-key "\C-cb" 'org-iswitchb)
