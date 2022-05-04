$(document).ready(function(){
    $('#id_date_end').mask('00/00/0000');
    $('#id_postal_code').mask('00.000-000');

    //$('#id_price_offer').mask('00000000,00');
    
    // Mask CPF and CNPJ
    $('#id_cpf_cnpj').mask('000.000.000-00', {
      onKeyPress : function(cpfcnpj, e, field, options) {
        const masks = ['000.000.000-000', '00.000.000/0000-00'];
        const mask = (cpfcnpj.length > 14) ? masks[1] : masks[0];
        $('#id_cpf_cnpj').mask(mask, options);
      }
    });

    //Brazil phone number
    var BRMaskBehavior = function (val) {
      return val.replace(/\D/g, '').length === 11 ? '(00) 00000-0000' : '(00) 0000-00009';
    },
    spOptions = {
      onKeyPress: function(val, e, field, options) {
          field.mask(BRMaskBehavior.apply({}, arguments), options);
        }
    };
    $('#id_phone_number').mask(BRMaskBehavior, spOptions);

  });

  //https://igorescobar.github.io/jQuery-Mask-Plugin/docs.html