$(function () {
    $('.block-select input[type="radio"]')
        .on('change', function () {
            if ($(this).prop('checked'))
                $(this).closest('.block-select').addClass('selected').siblings().removeClass('selected');
        })

    setTimeout(function () {
        $('.block-select input[type="radio"]').each(function () {
            // $(this).closest('.block-select').toggleClass('selected', $(this).prop('checked'))
            $(this).trigger('change')
        })
    }, 0)


    $('[name="delivery-or-pickup"]').on('change', function () {
        if ($(this).prop('checked'))
        {
            var type = $(this).val()
            $('[name="postal_code"]').parent().toggleClass('hidden', type == 'pickup');
            $('[name="city"]').parent().toggleClass('hidden', type == 'pickup');
            $('[name="address"]').parent().toggleClass('hidden', type == 'pickup');
        }
    })

    
    function format_price(price) { return price }


    var subtotal = parseFloat($('span[role="subtotal"]').text())

    var dl_home, dl_terminal

    function fill_shipping(response)
    {

        $('.order-step-3').addClass('visible')

        $('[shipping-method="post"]')
            .find('[role="total"]').text(format_price(subtotal + response['post_prepay'])).end()
            .find('[role="shipping-cost"]').text(format_price(response['post_prepay'])).end()

        $('[shipping-method="postpay"]')
            .find('[role="total"]').text(format_price(subtotal + response['post_postpay'])).end()
            .find('[role="shipping-cost"]').text(format_price(response['post_postpay'])).end()
            .find('[role="postpay_fee"]').text(format_price(response['post_postpay_fee'])).end()
        
        if (response['post_prepay'] == 0)
            $('[shipping-method="post"]').addClass('hidden')
        else
            $('[shipping-method="post"]').removeClass('hidden')
        if (response['post_postpay'] == 0)
            $('[shipping-method="postpay"]').addClass('hidden')
        else
            $('[shipping-method="postpay"]').removeClass('hidden')
        
        dl_home = dl_terminal = null;

        if (response.dl == null)
            $('[shipping-method="dl"]').addClass('hidden')
        else
        {
            var terminals_ul = $('[shipping-method="dl"] [role="terminals"]').empty()
            for (var i = 0; i < response.dl.terminals.length; i++)
            {
                var terminal = response.dl.terminals[i]
                $('<li>').append(
                    $('<a>')
                        .attr('href', terminal.link)
                        .attr('target', '_blank')
                        .html(terminal.address
                            .replace(/</g, '&lt;')
                            .replace(/>/g, '&gt;')
                            .replace(/"/g, '&quot;')
                            .replace(/([а-я]) (ул|ш|г|обл)/ig, '$1&nbsp;$2')
                        )
                )
                .appendTo(terminals_ul)
            }
            $('[shipping-method="dl"]')
                .removeClass('hidden')
                // .find('[role="total"]').text(format_price(subtotal + response['post_prepay'])).end()
                .find('[role="shipping-cost-home"]').text(format_price(response['dl']['cost_home'])).end()
                .find('[role="shipping-cost-terminal"]').text(format_price(response['dl']['cost_terminal'])).end()

            dl_home = response['dl']['cost_home']
            dl_terminal = response['dl']['cost_terminal']
            update_dl_cost()
        }
        if ($('[shipping-method]:not(.hidden)').size() == 0)
            $('[shipping-method="index_errors"]').removeClass('hidden')
        else
            $('[shipping-method="index_errors"]').addClass('hidden') 
            
        $('[name="shipping_cost_post"]').val(response['post_prepay']);
        $('[name="shipping_cost_postpay"]').val(response['post_postpay']);
        $('[name="shipping_cost_dl_home"]').val(dl_home);
        $('[name="shipping_cost_dl_terminal"]').val(dl_terminal);
    }


    function update_dl_cost()
    {
        var radios = $('[shipping-method="dl"] [name="dl_type"]')
        if (radios.filter(':checked').size() == 0)
            radios.first().prop('checked', true)

        var cost
        switch (radios.filter(':checked').val())
        {
            case 'home': cost = dl_home; break;
            case 'terminal': cost = dl_terminal; break;
        }

        $('[shipping-method="dl"] [role="total"]').text(format_price(subtotal + cost))
    }


    $('[shipping-method="dl"] [name="dl_type"]')
        .on('change', update_dl_cost)
        .on('click', function () {
            $('[name="shipping-method"][value="dl"]').prop('checked', true)
            $('[name="shipping-method"][value="dl"]').trigger('change')
        })



    var prev_index_value;
    $('[name="postal_code"]').on('change keyup', function () {
        var value = $(this).val();
        if (value == prev_index_value)
            return;

        prev_index_value = value;

        if (value.match(/^\d{6}$/))
        {
            $('.shipping-cost-loading').addClass('visible')

            setTimeout(function () {
                $.ajax({
                    method: 'POST',
                    url: '/order/testpost/',
                    dataType: 'json',
                    data: {
                        postindex: value
                    },

                    success: fill_shipping,

                    complete: function () {
                        $('.shipping-cost-loading').removeClass('visible')
                    }
                })
            }, 1);
        }
    }).trigger('change')



    var validators = {
        '[name="name"]': function (value) {
            if (! value)
                return 'Укажите ваши фамилию, имя и отчество';
            if (! value.match(/.* .* /))
                return 'Укажите полностью фамилию, имя и отчество';
            if (value.match(/.* .\.|.* .$/))
                return 'Укажите полностью фамилию, имя и отчество';
        },
        '[name="fio_pickup"]': function (value) {
            if (! value)
                return 'Укажите ваше имя';
        },

        '[name="email"]': function (value) {
            if (! value)
                return 'Укажите адрес электронной почты';
            if (! value.match(/.*@.*\./))
                return 'Проверьте правильность адреса';
        },
        '[name="phone"]': function (value) {
            if (! value || value == '+7')
                return 'Оставьте телефон для связи';
        },
        '[name="city"]': function (value) {
            if (! value) return 'Укажите населённый пункт';
        },
        '[name="address"]': function (value) {
            if (! value) return 'Укажите адрес доставки';
        },
        '[name="postal_code"]': function (value) {
            if (! value) return 'Индекс необходим для доставки';
            if (! value.match(/^\d{6}$/))
                return 'Индекс должен состоять из 6 цифр'
        }
    };


    var form = $('form.order-form');
    form.on('submit', function () {
        form.find('.validation-error').remove();

        var bad_inputs = [];

        for (var selector in validators)
            if (validators.hasOwnProperty(selector))
            {
                $(selector).filter(':visible').each(function () {
                    var $this = $(this);
                    var value = $this.val().trim();

                    var result = validators[selector](value);
                    if (result == null)
                        return;

                    var error_td = $('<span>').addClass('validation-error').text(result);
                    $this.closest('p').after(error_td);
                    bad_inputs.push($this);
                })
            }

        if (bad_inputs.length > 0)
        {
            var top_one = null;
            bad_inputs.forEach(function (el) {
                if (top_one == null || el.offset().top < top_one.offset().top)
                    top_one = el;
            });
            var target = top_one.offset().top - 100;
            if (window.scrollY > target)
                $.smoothScroll({offset: target});

            top_one.get(0).focus();

            return false;
        }


        var delivery_or_pickup = $('[name="delivery-or-pickup"]:checked').val();
        switch (delivery_or_pickup)
        {
            case null:
                return false;

            case 'delivery': {
                if ($('[name="shipping-method"]:checked').val() == null)
                {
                    alert('Выберите способ доставки');
                    return false;
                }
                break;
            }
        }
    })
})
