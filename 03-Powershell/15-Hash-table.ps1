$sana = [PSCustomObject]@{
    Name     = 'Kevin'
    Language = 'PowerShell'
    State    = 'Texas'
  }
  
  
  $sana.Name
  
  
  #############################################################
  
  Hash Table 
  $hash = @{}
  $hash = @{ Number = 1; Shape = "Square"; Color = "Blue"}
  
  $hash
  $hash.Keys
  $hash.Values
  

  return @{
    gagan = "love you"
}

  return [PSCustomObject]@{
    gagan = "loave you"
  }

    return [PSCustomObject]@{
    gagan = "loave you"
  } | ConvertTo-Json