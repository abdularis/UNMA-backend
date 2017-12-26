function setDataTable(table_tag) {
    $(table_tag).DataTable({
        'info': false,
        'language': {
            'lengthMenu': 'Tampilkan _MENU_ item',
            'zeroRecords': 'Maaf tidak ada data ditemukan!',
            'infoEmpty': 'Tidak ada record tersedia!'
        }
    });
}