((jQuery, window) => {
    'use strict';

    const BASE_ZINDEX = 1040;

    class MultiModal {
        constructor(element) {
            this.$element = jQuery(element);
            this.modalCount = 0;
        }

        show(target) {
            const $target = jQuery(target);
            const modalIndex = this.modalCount++;

            $target.css('z-index', BASE_ZINDEX + (modalIndex * 20) + 10);
            jQuery('.navbar-static-side').css('z-index', 'auto');

            window.setTimeout(() => {
                if (modalIndex > 0) {
                    jQuery('.modal-backdrop').not(':first').addClass('hidden');
                }
                this.adjustBackdrop();
            });
        }

        hidden(target) {
            this.modalCount--;
            jQuery('.navbar-static-side').css('z-index', 'auto');
            if (this.modalCount) {
                this.adjustBackdrop();
                jQuery('body').addClass('modal-open');
            }
        }

        adjustBackdrop() {
            const modalIndex = this.modalCount - 1;
            jQuery('.modal-backdrop:first').css('z-index', BASE_ZINDEX + (modalIndex * 20));
        }
    }

    jQuery.fn.multiModal = function (method, target) {
        return this.each(function () {
            let data = jQuery(this).data('multi-modal-plugin');
            if (!data) {
                jQuery(this).data('multi-modal-plugin', (data = new MultiModal(this)));
            }
            if (method) {
                data[method](target);
            }
        });
    };

    jQuery.fn.multiModal.Constructor = MultiModal;

    jQuery(document).on('show.bs.modal', (e) => {
        jQuery(document).multiModal('show', e.target);
    });

    jQuery(document).on('hidden.bs.modal', (e) => {
        jQuery(document).multiModal('hidden', e.target);
    });

})(jQuery, window);
