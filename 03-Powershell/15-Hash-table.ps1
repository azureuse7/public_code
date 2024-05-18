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
    gautam = "love you"
}

  return [PSCustomObject]@{
    gautam = "loave you"
  }

    return [PSCustomObject]@{
    gautam = "loave you"
  } | ConvertTo-Json