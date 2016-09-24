$(function() {

  populateTimeline(); // Populate the timeline
  renderConfigForm(); // Populate the configuration form
  renderAdvancedFilters(); // Populate the advanced filter form


  // Setting up nav-bar

  $('#menu-toggle').click(function(e) {
    e.preventDefault();
    $('#wrapper').toggleClass('toggled');
  });

  // Setting up datetime pickers

  $('#startDate').datetimepicker();
  $('#endDate').datetimepicker({
    useCurrent: false
  });
  $('#startDate').on('dp.change', function(e) {
    $('#endDate').data('DateTimePicker').minDate(e.date);
  });
  $('#endDate').on('dp.change', function(e) {
  $('#startDate').data('DateTimePicker').maxDate(e.date);
  });

  // Setting up show-all and hide-all buttons

  $('#showButton').click(function() {
    popAll();
  });
  $('#hideButton').click(function() {
    hideAll();
  });

  // Enable functionality for the first filter addition button in the advanced filter modal

  $('#addRemove1').click(function() {
    addField()
  })

  // Set up handlers for forms

  $('#advancedFiltersForm').submit(function(e) {
    e.preventDefault();
    $('#filterModal').modal('hide');
    if (!checkModal()) {
      $('#advancedFilter').attr('class', 'btn btn-success');
      $('#textFilter').attr('disabled', true);
      $('#textFilter').val('');
      saveFilters();
    } else {
      $('#advancedFilter').attr('class', 'btn btn-default');
      $('#textFilter').attr('disabled', false);
    }
  });

  $('#modal-x').click(function(e) {
    renderJsonFilters(getFilters());
  });

  $('#modal-close').click(function(e) {
    renderJsonFilters(getFilters());
  });

  $('#configForm').submit(function(e) {
    e.preventDefault();
    $.ajax({
      url: $(this).attr('action'),
      type: 'POST',
      data: $(this).serialize(),
      success: function(res) {
        console.log(res);
        $.ajax({
          url: $('#advancedFiltersForm').attr('action'),
          type: 'POST',
          data: $('#advancedFiltersForm').serialize(),
          success: function(res) {
            console.log(res);
            populateTimeline();
            renderConfigForm();
            renderAdvancedFilters();
          },
          error: function(error) {
            console.log(error);
          }
        });
      },
      error: function(error) {
        console.log(error);
      }
    });
  });

  // Allow clearing of the user options
  $('#clearConfig').click(function() {
    $.ajax({
      url: '/clearConfig',
      type: 'GET',
      success: function(res) {
        console.log(res);
        populateTimeline();
        renderConfigForm();
        renderAdvancedFilters();
      },
      error: function(error) {
        console.log(error);
      }
    });
  });


  // Add functionality to the color choice buttons
  $('*[class*=btn-empty]:visible').each(function() {
    $(this).click(function() {
      if ($(this).children().first().prop('checked')) {
        colorPull($(this));
      } else {
        colorPush($(this));
      };
    });
  });

});

// FUNCTIONS

function colorPush(c) {
  // Activates a color checkbox button
  c.children().first().button('toggle');
  c.children().first().prop('checked', true);
  c.children().first().prop('active', true);
  c.find('i').remove();
  c.append($('<i>').attr('class', 'glyphicon glyphicon-ok'));
}

function colorPull(c) {
  // Deactivates a color checkbox button
  c.children().first().button('toggle');
  c.children().first().prop('checked', false);
  c.children().first().prop('active', false);
  c.prop('active', false);
  c.find('i').remove();
}

function checkModal() {
  // checks whether any filters are inputted
  return (($('#count').attr('value') == 1) && ($('#filter1').val() == ''))
}

function saveFilters() {
  // Saved the current advancedFilters form input to the localStorage
  $.ajax({
    url: '/echoFilter',
    type: 'POST',
    data: $('#advancedFiltersForm').serialize(),
    success: function(res) {
      console.log(res);
      localStorage.setItem('tempForm', JSON.stringify(res));
    },
    error: function(error) {
      console.log(error);
    }
  });
}

function getFilters() {
  // Returns the currently saved advancedFilters form, parsed
  var filters = localStorage.getItem('tempForm');
  return JSON.parse(filters);
}

function renderJsonFilters(res) {
  // Renders the filter fields according to a JSON object
  $('#filterFields').empty();
  $('#count').attr('value', 0)
  if (res.length == 0) {
    addField();
    $('#advancedFilter').attr('class', 'btn btn-default');
    $('#textFilter').attr('disabled', false);
  } else {
    $('#advancedFilter').attr('class', 'btn btn-success');
    $('#textFilter').attr('disabled', true);
    $('#textFilter').val('');
  };
  for (i = 0; i < res.length; i ++) {
    addField()  
    var id = i + 1
    $('#required' + id).prop('checked', (res[i].is_required == 'on'));
    if (res[i].is_included == true) {
      $('#exclude' + id).attr('class', 'btn btn-success');
      $('#exclude' + id).text('Inc. ');
      $('#include' + id).val(true);
    } else {
      $('#exclude' + id).attr('class', 'btn btn-danger');
      $('#exclude' + id).text('Exc. ');
      $('#include' + id).val(false);
    };
    $('#filter' + id).val(res[i].text);
    $('#eventField' + id).val(res[i].field);
  };
}

function renderAdvancedFilters() {
  // Renders the advaced filter form according to the user_config
  $.ajax({
    url: '/getFilters',
    type: 'GET',
    success: function(res) {
      console.log(res);
      renderJsonFilters(res);
      saveFilters();
    },
    error: function(error) {
      console.log(error);
    }
  });
}

function renderConfigForm() {
  // Renders the config form according to the user_config
  $.ajax({
    url: '/getConfig',
    type: 'GET',
    success: function(res) {
      console.log(res);
      $('#startDate').val(res.start);
      $('#endDate').val(res.end);
      $('#ticks').val(res.textual_tick[0]);
      $('#unit').val(res.textual_tick[1]);
      $('#textFilter').val(res.filter);
      $('#tagSearch').tagsinput('removeAll');
      for (i=0;i < res.tags.length;i++) {
        $('#tagSearch').tagsinput('add', res.tags[i]);
      };
      $('*[class*=btn-empty]:visible').each(function() {
        var color = $(this).attr('class').match('btn btn-(.*) btn-empty')[1];
        if ($.inArray(color, res.colors) > -1) {
          colorPush($(this));
          $(this).addClass('active');
        } else {
          colorPull($(this));
          console.log(color);
        };
      });
    },
    error: function(error) {
      console.log(error);
    }
  });
}

function populateTimeline() {
  // Populate the timeline with events according to the user config
  $.ajax({
    url: '/getAllEvents',
    type: 'GET',
    success: function(res) {
      console.log(res)
      $('#time-line').empty()
      for (var i = 0; i < res.length; i++) {
        var isLast = (i == (res.length - 1));
        var event = createEvent(
          res[i].ID, 
          res[i].Title, 
          res[i].Description, 
          res[i].Time, 
          res[i].Icon, 
          res[i].Color, 
          Number(res[i].Space),
          (i % 2 == 0)?'right':'left',
          isLast);
        if (i == (res.length - 1)) {

        };
        event.click(function() {
          var id = $(this).attr('id').match(/\d+/);
          $('#tags' + id).off().click(function() {
            if ($('#tags' + id).attr('is-active') == 'true') {
              $.ajax({
                url: '/updateTags/' + id,
                type: 'POST',
                data: $('#tagField' + id).val(),
                success: function(res) {
                  console.log(res);
                  $('#tagField' + id).tagsinput('destroy');
                  $('#tagField' + id).remove();
                  $('#tags' + id).attr('is-active', 'false') 
                },
                error: function(error) {
                  console.log(error);
                }
              });
            } else {
              $.ajax({
                url: '/getTags/' + id,
                type: 'GET',
                success: function(res) {
                  console.log(res);
                  var tagsInput = $('<input>').attr({
                    'type' : 'text',
                    'class' : 'form-control',
                    'data-role' : 'tagsinput',
                    'id' : 'tagField' + id,
                    'name' : 'tagField' + id
                  });
                  tagsInput.val(res);
                  $('#popover' + id).append(tagsInput);
                  tagsInput.tagsinput('refresh');
                  $('#tags' + id).attr('is-active', 'true') 
                },
                error: function(error) {
                  console.log(error);
                }
              });
            };
          });          
        })
        $('#time-line').append(event)
      }
    },
    error: function(error) {
      console.log(error);
    }
  });
}

function popAll() {
  // Show all on-screen popovers
  $('*[class*=timeline-badge]:visible').filter(':onScreen').each(function() {
    $(this).popover('show');
  })
}

function hideAll() {
  // Hide all visible popovers
  $('*[class*=timeline-badge]:visible').each(function() {
    $(this).popover('hide');
  })
}

function createEvent(id, title, desc, time, icon, color, space, placement, isLast) {
  // Create a new timeline event object
  var content = '<small class="text-muted"><i class="glyphicon glyphicon-time"></i>&nbsp;' + time + '</small>' + '<p>' + desc + '</p>';
  var margin = String(60 * (space))
  var addedMargin = ""
  if (isLast) {
    addedMargin = 'margin-bottom: 60px; ';
  };
  var event = $('<li>').attr({
    'id' : 'event_' + id,
    'style' : 'margin-top: ' + margin + 'px; ' + addedMargin
  });
  var icon = $('<i>').attr({
    'class' : 'glyphicon glyphicon-' + icon
  });
  var title = title + '<button type="button" is-active="false" id="tags' + id + '" class="btn pull-right"><i class="glyphicon glyphicon-tags"></i></button>';
  var badge = $('<div>').attr({
    'class' : 'timeline-badge',
    'id' : 'timeline-badge' + id,
    'tooltip-time' : time,
    'popover-title' : title,
    'popover-content' : content
  });
  if (color != "undefined" && color != "NA") {
    badge.attr('class', 'timeline-badge ' + color);
  }

  badge.popover({
    content : badge.attr('popover-content'),
    title : badge.attr('popover-title'),
    html : true,
    template: '<div class="popover" role="tooltip"><div class="arrow"></div><h3 class="popover-title"></h3><div class="popover-content" id="popover' + id + '"><p></p></div></div>',
    placement : placement
  });

  badge.append(icon);
  event.append(badge);

  return event;
}

function fieldById(id) {
  // Creates a filter field DOM object according to its ID.
  // (Takes first field +/- into consideration)
  var div = $('<div>').attr({
    'id' : 'filterGroup' + id,
    'class' : 'input-group',
    'style' : 'margin-top: 5px;'
  });
  var requiredSpan = $('<span>').attr('class', 'input-group-addon');
  var requiredCheck = $('<input>').attr({
    'type' : 'checkbox',
    'id' : 'required' + id,
    'name' : 'required' + id
  });
  var inexDiv = $('<div>').attr('class', 'input-group-btn');
  var hiddenInex = $('<input>').attr({
    'type' : 'hidden',
    'id' : 'include' + id,
    'name' : 'include' + id,
  }).val(true);
  var inex = $('<button>').attr({
    'type' : 'button',
    'id' : 'exclude' + id, 
    'name' : 'exclude' + id,
    'class' : 'btn btn-success',
    'active' : false,
    'style' : 'border-top-left-radius: 0px; border-top-right-radius: 0px; border-bottom-left-radius: 0px; border-bottom-right-radius: 0px; width: 50px;'
  }).text('Inc. ');
  var filter = $('<input>').attr({
    'type' : 'text',
    'class' : 'form-control',
    'id' : 'filter' + id,
    'name' : 'filter' + id,
    'placeholder' : 'Filter',
    'style' : 'width: 80%'
  });
  var select = $('<select>').attr({
    'class' : 'form-control span2',
    'id' : 'eventField' + id,
    'name' : 'eventField' + id,
    'placeholder' : 'Field',
    'style' : 'width: 20%;'
  });
  var o1 = $('<option>').text('Title');
  var o2 = $('<option>').text('Text');
  var o3 = $('<option>').text('All');
  var buttonDiv = $('<div>').attr('class', 'input-group-btn');
  var buttonIcon = $('<i>').attr('class', 'glyphicon glyphicon-minus');
  var button = $('<button>').attr({
    'type' : 'button',
    'id' : 'addRemove' + id, 
    'field-counter' : id,
    'class' : 'btn btn-danger',
    'style' : 'border-top-left-radius: 0px; border-bottom-left-radius: 0px;'
  });
  if (id == '1') {
    var buttonIcon = $('<i>').attr('class', 'glyphicon glyphicon-plus');
    var button = $('<button>').attr({
      'type' : 'button',
      'id' : 'addRemove' + id, 
      'field-counter' : id,
      'class' : 'btn btn-success',
      'style' : 'border-top-left-radius: 0px; border-bottom-left-radius: 0px;'
    });
  }

  requiredSpan.append(requiredCheck);

  inex.click(function() {
    if (inex.attr('class') == 'btn btn-success') {
      hiddenInex.val(false);
      inex.attr('active', true);
      inex.attr('class', 'btn btn-danger');
      inex.text('Exc.');
    } else {
      hiddenInex.val(true);
      inex.attr('active', false);
      inex.attr('class', 'btn btn-success');
      inex.text('Inc. ');
    };
  });

  inexDiv.append(inex);

  select.append(o1);
  select.append(o2);
  select.append(o3);

  button.append(buttonIcon);
  if (id == 1) {
    button.click(function() {
      addField()
    })
  } else {
    button.click(function() {
      removeField(button.attr('field-counter'));
    });
  };
  buttonDiv.append(button);

  div.append(requiredSpan);
  div.append(inexDiv);
  div.append(filter);
  div.append(select);
  div.append(buttonDiv);
  div.append(hiddenInex);

  return div;
}

function addField() {
  // Add a new filter field to the advanced filter modal
  var id = String(Number($('#count').attr('value')) + 1)
  var div = fieldById(id);

  $('#count').attr('value', id)

  $('#filterFields').append(div);

  return div;
}

function removeField(id) {
  // Remove a field from the advanced filter modal
  $('#filterGroup' + id).remove();
  $('#count').attr('value', Number($('#count').attr('value')) - 1)
}
