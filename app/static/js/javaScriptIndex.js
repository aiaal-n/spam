/**
 * Created by user3 on 03.08.2017.
 */
 $('#selectAll').click(function (e) {
            var table = $(e.target).closest('table');
            $('td input:checkbox', table).prop('checked', this.checked);
        });
        $('#button_send').click(function () {
            var selectedIds = [];
            var selectedName = [];
            $('#myTable tr').filter(':has(:checkbox:checked)').each(function () {
                var i = parseInt($(this).closest('tr').attr('id'));
                if (!isNaN(i)) {
                    selectedIds.push(i);
                }
                if ($(this).closest('tr').children('td')[2] !== undefined) {
                    selectedName.push($(this).closest('tr').children('td')[2].innerText)
                }
            });
            var link = '/send';
            var dialog = $('#modal-send');
            dialog.find('form').attr('action', link);
            dialog.modal().css({
                width: 'auto'
            });
            dialog.modal('show');
            document.getElementById("text-org").textContent = selectedName;
            document.getElementById("text-org").innerHTML = document.getElementById("text-org").textContent.replaceAll(",", "<br>")
            $('#list_id').val(selectedIds)
        });
        function confirmUpdate(event) {
            var id = $(event.target).attr('id');
            window.location = '/update/?id=' + id;
        }
        $('#button_delete').click(function () {
           console.log("pagi");
        });
        $('#button_delete').click(function () {
            var selectedIds = [];
            var selectedName = [];
            $('#myTable tr').filter(':has(:checkbox:checked)').each(function () {
                selectedIds.push($(this).closest('tr').attr('id'));
                if (selectedIds[0] == undefined) {
                    selectedIds.splice(0, 1)
                }
                if ($(this).closest('tr').children('td')[2] != undefined) {
                    selectedName.push($(this).closest('tr').children('td')[2].innerText)
                }
            });
            var link = '/delete';
            var dialog = $('#modal-delete');
            dialog.find('form').attr('action', link);

            dialog.modal('show');
            document.getElementById("text-modal").textContent = selectedName;
            document.getElementById("text-modal").innerHTML = document.getElementById("text-modal").textContent.replaceAll(",", "<br>")
            console.log(document.getElementById("text-modal").innerHTML)
            $('#list_id_del').val(selectedIds)
        });
        String.prototype.replaceAll = function (token, newToken, ignoreCase) {
            var _token;
            var str = this + "";
            var i = -1;
            if (typeof token === "string") {
                if (ignoreCase) {
                    _token = token.toLowerCase();
                    while ((
                        i = str.toLowerCase().indexOf(
                            _token, i >= 0 ? i + newToken.length : 0
                        ) ) !== -1
                        ) {
                        str = str.substring(0, i) +
                            newToken +
                            str.substring(i + token.length);
                    }
                } else {
                    return this.split(token).join(newToken);
                }
            }
            return str;
        };
        $('input[type=checkbox]').change(function () {
            var len = $('input[type=checkbox]:checked').length
            if (len > 0) {
                $('#button_send').attr("disabled", false).removeClass('disabled');
                $('#button_delete').attr("disabled", false).removeClass('disabled');
            }
            else {
                $("#button_send").attr("disabled", true).addClass('disabled');
                $('#button_delete').attr("disabled", true).addClass('disabled');
            }
        });

        function removeTemplate() {
            var $target = $(this);
            var id = $target.data('id');
            $target.remove();

            var $badge = $('#templates_available').find('.list-group-item[data-id="' + id + '"]').find('.badge');
            var count = parseInt($badge.html());
            if ((isNaN(count)) || (count === 1)) {
                $badge.html('');
            } else {
                $badge.html(count - 1);
            }
        }
        function addTemplate() {
            var $target = $(this);

            var $input = $('<input>', {'type': 'hidden', 'name': 'template', 'value': $target.data('id')});

            $('<a />', {'href': '#', 'class': 'list-group-item', 'data-id': $target.data('id')})
                .append($('<span />').html($target.data('value')))
                .append($input)
                .appendTo('#templates_selected');
        }

        $('#templates_available').on('click', '.list-group-item', addTemplate);
        $('#templates_selected').on('click', '.list-group-item', removeTemplate);

        function Search() {
            var input, filter, table, tr, td, i;
            input = document.getElementById("myInput");
            filter = input.value.toUpperCase();
            table = document.getElementById("myTable");
            tr = table.getElementsByTagName("tr");
            for (i = 0; i < tr.length; i++) {
                td = tr[i].getElementsByTagName("td")[2];
                if (td) {
                    if (td.innerHTML.toUpperCase().indexOf(filter) > -1) {
                        tr[i].style.display = "";
                    } else {
                        tr[i].style.display = "none";
                    }
                }
            }
        }